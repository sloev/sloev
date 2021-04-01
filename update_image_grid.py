import json
import os
import clickcounter
from lxml import etree
import random

provider = clickcounter.LinkClickCounterCom()

img_prefix = "https://raw.githubusercontent.com/sloev/sloev/master/.github/images"


def create_grid(
    image_cycle,
    width,
    height,
    url,
    username,
    password,
    size=15,
):
    provider.login(username, password)

    output_html = ""
    for y in range(height):
        if output_html:
            output_html += "<br>"

        for x in range(width):
            img_src = random.choice(image_cycle)
            track_url = provider.register_url(url)
            output_html += f'<a title="y={y}, x={x}" href="{track_url}"><img src="{img_src}" width="{size}px" height="{size}px"/></a>'
    return "\n\n".join(["<!-- grid_begin -->", output_html, "<!-- grid_end -->"])


def get_counts(username, password):
    provider.login(username, password)
    rows = provider.get_all_visits()
    return rows


def cycle_imgs(markdown_text, image_cycle, username, password, size=15):
    counts = get_counts(username, password)

    def next_val(val, count):
        incr = count % len(image_cycle)
        i = image_cycle.index(val)
        i += incr
        if i >= len(image_cycle):
            i -= len(image_cycle)
        return image_cycle[i]

    before_text, html = markdown_text.split("<!-- grid_begin -->")
    html, after_text = html.split("<!-- grid_end -->")
    html = html.strip()
    output_html = ""
    for row_html in html.split("<br>"):
        row_html = "<div>" + row_html + "</div>"
        doc = etree.fromstring(row_html)
        for link in doc.xpath("//a"):
            href = link.get("href")
            title = link.get("title")
            img_src = link.xpath("//img/@src")[0]

            img_src = next_val(img_src, counts[href])
            output_html += f'<a title="{title}" href="{href}"><img src="{img_src}" width="5%"/></a>'
    return "\n".join(
        [
            before_text.rstrip(),
            "<!-- grid_begin -->\n",
            output_html,
            "\n<!-- grid_end -->",
            after_text.lstrip(),
        ]
    )


username = os.environ["EMAIL"]
password = os.environ["PASSWORD"]
image_cycle = ["{}/{:03}.png".format(img_prefix, i) for i in range(1,38)]
# markdown_text = create_grid(image_cycle, 15, 5, "https://github.com/sloev",
#                             username, password)

markdown_text = open("README.md").read()


new_markdown_text = cycle_imgs(markdown_text, image_cycle, username, password)

with open("README.md", "w") as f:
    f.write(new_markdown_text)
