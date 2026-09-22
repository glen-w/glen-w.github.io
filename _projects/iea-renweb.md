---
layout: page
title: IEA-Renweb
description: Turn an IEA World Energy Balances extract into renewable energy statistics.
img: /assets/img/projects/thumbs/iea_renweb.png
importance: 2
category: archive
github: https://github.com/glen-w/IEA-Renweb
docs: https://github.com/glen-w/IEA-Renweb/blob/main/docs/METHODOLOGY.md
---

<div align="center">
  <img src="/assets/img/projects/thumbs/iea_renweb.png" alt="IEA-Renweb logo" width="160"/>
</div>

The IEA World Energy Balances are the table you want and cannot casually share. They are large, paid-for, and not in a shape that gives you renewable shares or sector splits.

IEA-Renweb is what I run when I already have an extract. It is a library and a command-line tool, not a website. The balances stay out of the project; I point it at files I downloaded.

It checks units and leaves bad rows out. It calculates total final energy consumption, renewable and fossil shares, and the usual sector splits. Other datasets can sit alongside without changing the IEA identities.

I do not treat this as an active product. I reach for it when I have a balances file and need the statistics.
