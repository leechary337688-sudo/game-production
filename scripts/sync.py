#!/usr/bin/env python3
"""Re-sync this repository from the public SkillsBot JSON API.

Scope (per requester): Unity / Unreal / Godot / Blender related skills, plus
game design, numbers (数值), narrative (剧情) and art pipeline (美术管线).
Medical, elderly-care, sales, reverse-engineering / hacking content is dropped.
Duplicate listings are merged by en_name.

Usage:
    python scripts/sync.py                 # full sync (categories + keyword search)
    python scripts/sync.py --skip-search   # only the game categories
    python scripts/sync.py --categories 209 252 --max-pages 1 --out /tmp/demo

The script only calls the same public, unauthenticated endpoints the site
itself uses. It writes skills/, catalog/, index.json and README.md.

Notes
-----
* SkillsBot's zip download requires a logged-in account with download quota,
  so this script collects the published skill body (SKILL.md) only.
* Requests are paced sequentially to stay polite; a full run takes a few
  minutes and resumes from the local cache directory.
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.skillsbot.cn/skillv3/api/github"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

GAME_CATEGORIES = {
    209: "游戏开发",
    249: "三维与游戏",
    250: "Blender建模",
    251: "Maya动画",
    252: "Unity开发",
    253: "Unreal Engine",
    255: "游戏策划",
    256: "角色设计",
    257: "场景建模",
    258: "动作捕捉",
    259: "游戏测试",
    445: "游戏策划",
    465: "游戏设计",
}
GAME_CATS = set(GAME_CATEGORIES)
GAME_NAMES = set(GAME_CATEGORIES.values()) | {"游戏设计"}

SEARCH_KEYWORDS = [
    "游戏", "游戏开发", "游戏设计", "游戏策划", "游戏测试", "游戏运营",
    "Unity", "Unreal", "Godot", "Blender", "Maya",
    "3D", "像素", "关卡", "战斗", "数值", "玩法", "玩家", "电竞", "RPG",
    "美术", "动画", "音效", "角色设计", "独立游戏",
]

# Curated by hand from keyword-search results (outside the game categories).
EXTRAS = [121, 4495, 4496, 7365, 7367, 8955, 12484]
EXTRA_GROUPS = {
    "游戏美术与叙事": {"character-design-sheet", "storyboard-generator", "art-style-creator", "character-naming"},
    "游戏开发": {"game-developer", "combat-system-creator"},
}
EXTRA_SKILL_NAMES = set().union(*EXTRA_GROUPS.values())
GROUP_ORDER = ["游戏开发", "Unity开发", "Unreal Engine", "Blender建模", "Maya动画",
               "角色设计", "场景建模", "动作捕捉", "游戏策划", "游戏设计",
               "游戏美术与叙事"]
SUBCATEGORIES = {"Blender建模", "Maya动画", "Unity开发", "Unreal Engine", "游戏策划",
                 "角色设计", "场景建模", "动作捕捉", "游戏测试", "游戏设计"}

# ---- scope filter ----------------------------------------------------------
KEEP_ENGINE = [
    "unity", "unreal", "虚幻", "ue4", "ue5", "godot", "blender", "gdscript",
    "shader", "着色器", "hlsl", "glsl", "渲染", "光照", "材质", "纹理", "贴图",
    "动画", "绑定", "骨骼", "蒙皮", "角色", "建模", "场景", "地形", "特效",
    "粒子", "后处理", "lumen", "nanite", "niagara", "metasounds", "sequencer",
    "cinemachine", "probuilder", "addressables", "tilemap", "mecanim",
    "蓝图", "blueprint", "hud", "ui toolkit", "ui界面", "input system",
    "physics", "物理", "ragdoll", "布料", "流体", "terrain", "lod", "遮挡",
    "decal", "贴花", "pbr", "raytracing", "光线追踪", "阴影", "shadow",
    "世界构成", "world composition", "motion matching", "根运动",
    "动作匹配", "maya", "zbrush", "substance", "houdini", "facial",
    "资产", "破坏", "瓦片", "程序化生成", "visual effect",
]
KEEP_DESIGN = [
    "游戏设计", "策划", "机制", "数值", "平衡", "经济", "economy", "balance",
    "progression", "成长", "奖励", "战斗", "combat", "剧情", "叙事",
    "narrative", "story", "故事", "任务", "quest", "对话", "dialogue",
    "关卡", "level", "玩法", "gameplay", "gdd", "核心循环", "core loop",
    "美术", "art", "风格", "storyboard", "分镜", "角色设计", "character",
    "命名", "naming", "探索", "exploration", "游戏机制",
]
KEEP_CATEGORIES = {
    "Unity开发", "Unreal Engine", "Blender建模", "Maya动画", "角色设计",
    "场景建模", "动作捕捉", "游戏策划", "游戏设计", "战斗系统设计",
    "品牌设计", "AIGC",
}
DROP_NAMES = {
    "ab-testing", "accessibility-games", "game-analytics", "player-retention",
    "remote-config", "lobby-system", "matchmaking", "enet", "p2p-networking",
    "state-sync", "lag-compensation", "git-lfs", "perforce", "steam-sdk",
    "steamworks-networking", "epic-sdk", "gog-sdk", "playstation-sdk",
    "switch-sdk", "xbox-gdk", "allaymc-plugin-dev", "vulkan-compute",
    "graphics-api-hooking", "threejs-pro", "threejs-animation",
    "threejs-builder", "web-games", "develop-web-game", "2d-games",
    "3d-games", "pc-games", "mobile-games", "vr-ar", "multiplayer",
    "game-development", "gamedev-expert", "cocos2d-x", "construct", "defold",
    "gamemaker", "phaser", "luatablespatterns", "dart-python", "jutsu-creator",
    "gpui-action", "8bit-docs-patterns", "slack-gif-creator",
    "visual-and-observational-rules", "machine", "grasshopper-workflow",
    "astar", "steering-behaviors", "touch-controls", "fsm", "voice-chat",
}
FORBIDDEN = ["医疗", "养老", "销售", "逆向", "黑客", "作弊", "外挂",
             "hack", "cheat", "反作弊", "anti-cheat"]


def norm(text):
    return (text or "").lower()


def in_scope(skill):
    en = norm(skill.get("en_name")).strip()
    name_blob = " ".join([norm(skill.get("name")), en])
    blob = " ".join([name_blob, norm(skill.get("description")),
                     norm(skill.get("category"))])
    if en in DROP_NAMES:
        return False
    if any(word in name_blob for word in FORBIDDEN):
        return False
    if skill.get("category") in KEEP_CATEGORIES:
        return True
    if any(word in blob for word in KEEP_ENGINE):
        return True
    return any(word in blob for word in KEEP_DESIGN)


def merge_duplicates(skills):
    keyed = {}
    for s in skills:
        key = norm(s.get("en_name")).strip() or re.sub(r"\s+", "", norm(s.get("name")))
        keyed.setdefault(key or f"id-{s['id']}", []).append(s)
    merged = []
    for group in keyed.values():
        group.sort(key=lambda s: (-len(s.get("content") or ""),
                                  -int(s.get("installs") or 0), s["id"]))
        main = dict(group[0])
        main["merged_ids"] = [s["id"] for s in group if s["id"] != main["id"]]
        found = []
        for s in group:
            for v in s.get("found_via") or []:
                if v not in found:
                    found.append(v)
        main["found_via"] = found
        main["installs"] = max(int(s.get("installs") or 0) for s in group)
        main["views"] = max(int(s.get("views") or 0) for s in group)
        merged.append(main)
    return merged


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep([5, 20, 45, 90][attempt])
    raise last


def slugify(text, fallback):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text).strip("-.")
    text = re.sub(r"-{2,}", "-", text)
    return text or fallback


def display_name(name, sid):
    name = (name or "").strip() or f"Skill {sid}"
    if name.endswith("Skill") and len(name) > 5:
        name = name[:-5].rstrip()
    return name


def collect(cache_dir, categories, keywords, max_pages, skip_search):
    os.makedirs(os.path.join(cache_dir, "details"), exist_ok=True)
    records, provenance = {}, {}

    for cat in categories:
        page = 1
        while page <= max_pages:
            try:
                data = fetch(f"{BASE}/file/category/{cat}/page/{page}").get("data") or {}
            except Exception as exc:  # noqa: BLE001
                print(f"  category {cat} page {page} failed: {exc}", file=sys.stderr)
                break
            recs = data.get("records") or []
            for rec in recs:
                rid = str(int(rec["id"]))
                records[rid] = rec
                provenance.setdefault(rid, [])
                if f"category:{cat}" not in provenance[rid]:
                    provenance[rid].append(f"category:{cat}")
            if not recs or len(recs) < 12:
                break
            page += 1
            time.sleep(0.4)

    if not skip_search:
        for kw in keywords:
            q = urllib.parse.quote(kw)
            page = 1
            while page <= max_pages:
                try:
                    data = fetch(f"{BASE}/file/search?current={page}&size=12&keyword={q}").get("data") or {}
                except Exception as exc:  # noqa: BLE001
                    print(f"  search {kw!r} page {page} failed: {exc}", file=sys.stderr)
                    break
                recs = data.get("records") or []
                for rec in recs:
                    rid = str(int(rec["id"]))
                    records[rid] = rec
                    provenance.setdefault(rid, [])
                    if f"search:{kw}" not in provenance[rid]:
                        provenance[rid].append(f"search:{kw}")
                if not recs or len(recs) < 12:
                    break
                page += 1
                time.sleep(0.4)

    for rid in set(EXTRAS):
        records.setdefault(str(rid), {})
        provenance.setdefault(str(rid), []).append("curated:extra")

    return records, provenance


def get_details(cache_dir, ids):
    todo = [i for i in ids
            if not os.path.exists(os.path.join(cache_dir, "details", f"{i}.json"))]
    print(f"details to fetch: {len(todo)}")

    def work(sid):
        try:
            data = fetch(f"{BASE}/file/{sid}")
            detail = (data or {}).get("data")
            if detail:
                with open(os.path.join(cache_dir, "details", f"{sid}.json"), "w", encoding="utf-8") as fh:
                    json.dump(detail, fh, ensure_ascii=False, indent=1)
                return True
        except Exception as exc:  # noqa: BLE001
            print(f"  detail {sid} failed: {exc}", file=sys.stderr)
        return False

    # sequential + paced: the detail endpoint rate-limits bursts
    ok = 0
    for i, sid in enumerate(todo, 1):
        if work(sid):
            ok += 1
        if i % 20 == 0:
            print(f"  {i}/{len(todo)} fetched")
        time.sleep(1.2)
    print(f"details fetched: {ok}/{len(todo)}")


def build(out_dir, cache_dir, records, provenance):
    def load_detail(sid):
        path = os.path.join(cache_dir, "details", f"{sid}.json")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as fh:
            detail = json.load(fh)
        if isinstance(detail, dict) and isinstance(detail.get("data"), dict):
            detail = detail["data"]
        return detail

    extras = {str(i) for i in EXTRAS}
    skills = []
    for sid, rec in records.items():
        detail = load_detail(sid)
        if not detail:
            continue
        record = rec or detail
        is_extra = sid in extras
        if not is_extra and int(detail.get("categoryId") or record.get("categoryId") or 0) not in GAME_CATS:
            continue
        cats = {detail.get("categoryName"), detail.get("parentCategoryName")}
        if not (cats & GAME_NAMES or (record.get("enName") or "") in EXTRA_SKILL_NAMES):
            continue
        cat = detail.get("categoryName") or ""
        en_name = (detail.get("enName") or record.get("enName") or "").strip()
        if is_extra:
            group = next((g for g, names in EXTRA_GROUPS.items() if en_name in names), cat or "其他")
        else:
            group = cat if cat in SUBCATEGORIES else (cat or "其他")
        skills.append({
            "id": int(sid),
            "name": display_name(detail.get("name") or record.get("name"), sid),
            "en_name": en_name,
            "category": cat,
            "parent_category": detail.get("parentCategoryName") or "",
            "group": group,
            "description": (detail.get("description") or record.get("description") or "").strip(),
            "installs": detail.get("downloadCount") or record.get("downloadCount") or 0,
            "views": detail.get("viewCount") or record.get("viewCount") or 0,
            "updated": (detail.get("updateTime") or record.get("updateTime") or "")[:10],
            "content": (detail.get("detail") or "").strip(),
            "original_name": detail.get("originalName") or "",
            "file_size": detail.get("fileSize") or 0,
            "github_project": detail.get("githubProjectName") or "",
            "url": f"https://www.skillsbot.cn/skill/{sid}",
            "found_via": provenance.get(sid, []),
            "extra": is_extra,
        })

    skills = merge_duplicates([s for s in skills if in_scope(s)])
    print(f"in scope: {len(skills)} skills")

    used = set()
    for s in sorted(skills, key=lambda x: (-int(x["installs"]), x["id"])):
        base = slugify(s["en_name"], f"skill-{s['id']}")
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        s["slug"] = slug

    skills_dir = os.path.join(out_dir, "skills")
    if os.path.isdir(skills_dir):
        shutil.rmtree(skills_dir)
    os.makedirs(skills_dir, exist_ok=True)
    for s in skills:
        d = os.path.join(skills_dir, s["slug"])
        os.makedirs(d, exist_ok=True)
        content = s["content"]
        if not content.startswith("---"):
            fm = ["---", f"name: {s['en_name'] or s['slug']}",
                  f"description: {json.dumps(s['description'], ensure_ascii=False)}", "---", ""]
            content = "\n".join(fm) + content
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write(content.rstrip() + "\n")
        meta = {k: s[k] for k in (
            "id", "name", "en_name", "category", "parent_category", "description",
            "installs", "views", "updated", "original_name", "file_size",
            "github_project", "url", "found_via", "merged_ids",
        ) if k in s}
        with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = {
        "generated_at": generated,
        "source": "https://www.skillsbot.cn",
        "source_note": "SkillsBot AI Skill 技能库：游戏开发 / 三维与游戏 分类，以及游戏相关关键词搜索。",
        "scope": "Unity / Unreal / Godot / Blender 相关，以及游戏设计、数值、剧情、美术管线类技能；"
                 "已剔除医疗、养老、销售、逆向/黑客等无关内容，重复项按 en_name 合并。",
        "total": len(skills),
        "skills": [{k: s[k] for k in (
            "id", "name", "en_name", "slug", "group", "category",
            "description", "installs", "views", "updated", "url")} | {"path": f"skills/{s['slug']}/SKILL.md"}
                   for s in skills],
    }
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    groups = {}
    for s in skills:
        groups.setdefault(s["group"], []).append(s)
    order = sorted(groups, key=lambda g: (0, GROUP_ORDER.index(g)) if g in GROUP_ORDER else (1, g))

    cat_dir = os.path.join(out_dir, "catalog")
    if os.path.isdir(cat_dir):
        shutil.rmtree(cat_dir)
    os.makedirs(cat_dir, exist_ok=True)
    for g in order:
        rows = sorted(groups[g], key=lambda x: (-int(x["installs"]), x["name"]))
        lines = [f"# {g}（{len(rows)} 个技能）", "", "| 技能 | 简介 | 安装量 | 来源 |", "|---|---|---|---|"]
        for s in rows:
            desc = s["description"].replace("|", "\\|").replace("\n", " ")
            if len(desc) > 110:
                desc = desc[:110] + "…"
            lines.append(f"| [{s['name']}](../skills/{s['slug']}/) | {desc} | {s['installs']} | "
                         f"[SkillsBot #{s['id']}]({s['url']}) |")
        lines += ["", "<sub>返回 [README](../README.md)</sub>"]
        fn = re.sub(r'[\\/:*?"<>|]', "-", g) + ".md"
        with open(os.path.join(cat_dir, fn), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    top = sorted(skills, key=lambda x: -int(x["installs"]))[:15]
    readme = [
        "# game-production",
        "",
        "游戏生产（Game Production）相关的 AI Agent Skills 合集，按「游戏开发 / 三维与游戏」方向整理，"
        "可直接复制到支持 Skills 的 Agent 中使用。",
        "",
        "## 数据来源",
        "",
        "全部技能来自 **SkillsBot**（<https://www.skillsbot.cn>）的公开检索：",
        "",
        "- 分类：`游戏开发`、`三维与游戏`（含 Blender建模、Maya动画、Unity开发、Unreal Engine、"
        "游戏策划、角色设计、场景建模、动作捕捉、游戏测试）",
        "- 关键词搜索：游戏、游戏开发、游戏设计、游戏策划、游戏测试、游戏运营、Unity、Unreal、Godot、"
        "Blender、Maya、3D、像素、关卡、战斗、数值、玩法、玩家、RPG、动画、音效、角色设计、独立游戏 等",
        "- 收录范围：仅保留 **Unity / Unreal / Godot / Blender** 相关技能，以及 **游戏设计、数值、剧情、"
        "美术管线** 这几类；已剔除医疗、养老、销售、逆向/黑客等无关内容，重复技能按名称合并",
        f"- 抓取时间：{generated}",
        "",
        "## 仓库结构",
        "",
        "```",
        "skills/<技能名>/SKILL.md   技能正文（从 SkillsBot 公开详情接口获取）",
        "skills/<技能名>/meta.json  分类、安装量、原始项目、来源链接",
        "catalog/*.md               按分类整理的技能索引",
        "index.json                 机器可读索引",
        "scripts/sync.py            重新检索并同步（复现本仓库）",
        "```",
        "",
        "## 分类统计",
        "",
        "| 分类 | 技能数 | 索引 |",
        "|---|---|---|",
    ]
    for g in order:
        fn = re.sub(r'[\\/:*?"<>|]', "-", g) + ".md"
        readme.append(f"| {g} | {len(groups[g])} | [catalog/{fn}](catalog/{fn}) |")
    readme += [f"| **合计** | **{len(skills)}** | |", "", "## 安装量最高的技能", "",
               "| # | 技能 | 分类 | 安装量 |", "|---|---|---|---|"]
    for i, s in enumerate(top, 1):
        readme.append(f"| {i} | [{s['name']}](skills/{s['slug']}/) | {s['group']} | {s['installs']} |")
    readme += [
        "",
        "## 使用方式",
        "",
        "技能目录遵循常见的 Agent Skills 约定（`SKILL.md` + YAML frontmatter）。",
        "",
        "```bash",
        "# 方式一：整个目录拷进你的 Agent 技能目录",
        "git clone https://github.com/leechary337688-sudo/game-production.git",
        "cp -r game-production/skills/* ~/.claude/skills/",
        "",
        "# 方式二：只取需要的技能",
        "cp -r game-production/skills/godot-master ~/.claude/skills/",
        "```",
        "",
        "## 说明与限制",
        "",
        "- SkillsBot 的技能正文为其中文译文，原始技能来自开源社区；"
        "每个技能的来源、原始项目名和安装量记录在 `skills/<技能名>/meta.json`。",
        "- 同一技能在 SkillsBot 上可能有重复条目，已按 `en_name` 合并，被合并的条目 id 记录在 "
        "`meta.json` 的 `merged_ids` 中（若存在）。",
        "- 本仓库只收录**正文（SKILL.md）**。部分技能在 SkillsBot 上还有附带资源文件，"
        "需要在 SkillsBot 登录后下载完整包（下载有次数限制）。",
        "- 技能正文的版权归原作者；本仓库仅做检索整理，便于游戏项目直接取用。"
        "仓库自身的索引、脚本以 MIT 协议提供。",
        "",
    ]
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(readme))

    projects = sorted({s["github_project"] for s in skills if s["github_project"]})
    lines = ["# 来源与致谢", "",
             "本仓库技能正文来自 SkillsBot（https://www.skillsbot.cn）公开详情接口，"
             "SkillsBot 收录并翻译自开源社区。", "",
             "| 技能 | 来源页面 | 原始项目/作者 |", "|---|---|---|"]
    for s in sorted(skills, key=lambda x: x["name"]):
        lines.append(f"| {s['name']} | {s['url']} | {s['github_project'] or '未标注'} |")
    lines += ["", f"共 {len(skills)} 个技能，涉及 {len(projects)} 个可识别的原始项目。", ""]
    with open(os.path.join(out_dir, "ATTRIBUTION.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"built {len(skills)} skills, {len(groups)} groups -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Sync game-production skills from skillsbot.cn")
    parser.add_argument("--out", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser.add_argument("--cache", default=".cache")
    parser.add_argument("--categories", type=int, nargs="*", default=sorted(GAME_CATEGORIES))
    parser.add_argument("--keywords", nargs="*", default=SEARCH_KEYWORDS)
    parser.add_argument("--max-pages", type=int, default=60)
    parser.add_argument("--skip-search", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.cache, exist_ok=True)
    records, provenance = collect(args.cache, args.categories, args.keywords,
                                  args.max_pages, args.skip_search)
    ids = [i for i in records
           if str(int(records[i].get("categoryId") or 0)) in {str(c) for c in GAME_CATS}
           or str(int(i)) in {str(e) for e in EXTRAS}]
    get_details(args.cache, ids)
    build(args.out, args.cache, records, provenance)


if __name__ == "__main__":
    main()
