import frontmatter, datetime as dt
from backend.services.vault_watcher import FEATURES_DIR

def append_to_note(title: str, md_block: str):
    fn = next(FEATURES_DIR.glob(f"*{slugify(title)}*.md"), None)
    if not fn:
        # new file
        today = dt.date.today().isoformat()
        fn = FEATURES_DIR/ f"{today}-{slugify(title)}.md"
        post = frontmatter.Post(md_block, **{"title": title, "status": "active"})
    else:
        post = frontmatter.load(fn)
        post.content += "\n\n" + md_block
    frontmatter.dump(post, fn.open("w", encoding="utf-8"))

def slugify(s): return s.lower().replace(" ", "-")
