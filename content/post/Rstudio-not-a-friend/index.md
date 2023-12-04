---
title: "Rstuio is not a friend of HugoBlox"
author: YUNWEI HU
date: '2023-12-03'
tags:
- Markdown
---

Well, this is probably obvious.If you've wandered through the HugoBlox documentation, you've likely stumbled upon this cautionary note:

> The RStudio team released Blogdown, a wrapper around Hugo for the RStudio IDE. However, users report that Blogdown doesn’t fully support modern Hugo versions, with the RStudio team confirming these bug reports on GitHub. Therefore, it’s not currently recommended to use Blogdown. Also, as Blogdown is an extra tool in the workflow, it can add unnecessary additional complexity to projects.

The journey of migrating old blog posts crafted with blogdown to the sleek hugoblox platform is far from straightforward. And for those of us looking to author future posts using Rmarkdown, the path isn't exactly linear.

Here's the crux: blogdown isn't the recommended tool anymore. Instead, we're advised to start our posts as R notebooks or R Markdown files. Then, we should heed the guidance from the HugoBlox documentation:

> It’s recommended to convert RMarkdown files directly to Markdown without Blogdown by using `render("input.Rmd", md_document())` or adding `output: md_document` to the file’s front matter.

One tricky aspect is the header of markdown file, which isn't processed by `Rmarkdown::render()`. This means we have to manually recreate the header details—like the title and author—and ensure all images and associated files are meticulously placed in their proper directories.

It's a bittersweet transition away from `blogdown`, carrying both the promise of a streamlined process and the pain of leaving a familiar tool behind. 

Here's to embracing change and the adventures that await in the blogging realm!