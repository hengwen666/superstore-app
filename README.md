# Global Superstore Sales Monitor

> **Team name:** `zhaoyile`
>
> **Deployed app:** `https://superstore-app-22a6aapthwqm2vh89yrcbp.streamlit.app/`
>
> **Repository:** `https://github.com/hengwen666/superstore-app`

A small Streamlit dashboard built around one decision-maker — the **regional sales
manager** of the Global Superstore chain. It deliberately shows only three
headline numbers and two supporting charts, because every extra chart makes the
important ones harder to find.

---

## Step 1 — Dataset and Decision-Maker

**Dataset:** *Global Super Store Dataset* on Kaggle —
<https://www.kaggle.com/datasets/apoorvaappz/global-super-store-dataset>

- **Where it comes from:** the Tableau "Global Superstore" sample dataset,
  published on Kaggle. It is **illustrative/synthetic data**, not a real
  retailer's transactions, so the findings are about this dataset rather than a
  real company.
- **Period covered:** orders placed **1 Jan 2011 – 31 Dec 2014** (four years;
  despite the "2015" in some filenames, the last order date is in 2014).
- **One row = one order line item** (one product on one order). There are
  **51,290 rows** across **7 markets** (APAC, LATAM, EU, US, EMEA, Africa,
  Canada) and 25,035 distinct orders.
- **File preparation:** the original download has 24 columns. I kept the 14
  columns needed for the decisions (order date, market, region, country,
  segment, category, sub-category, sales, quantity, discount, profit, shipping
  cost, order priority) and dropped 10 that add no decision value — row id,
  customer id/name, product id/name, ship date, ship mode, city, state and
  postal code. This shrinks the committed file from ~12 MB to ~5.5 MB and
  removes the mostly-empty `Postal Code` column.

**Decision-maker:** the **regional sales manager** for one market (the app
defaults to the **US** market, which is the 9,994-row / 5,009-order
US business). This is a specific role, not "everyone."

## Step 2 — Justify the Dashboard

1. **Who looks at it, and how often?** The regional sales manager, every
   **Monday morning** when planning the week's promotions and restock, plus a
   quick glance at the headline numbers each day.
2. **What decision does it support?**
   > *"If the regional sales manager sees a product line running at a loss
   > (or a profit margin dropping in a region) on this dashboard, they will cut
   > its discount or change its promotion that week."*
3. **What do they do today, and what does it cost?** Today someone pulls the
   orders spreadsheet, builds a pivot table and emails a static slide once a
   week. That is a day of analyst time, and the numbers are already a week old
   when the manager sees them — a bad discount can run for another week before
   anyone notices.
4. **Why a dashboard rather than a weekly email / report / alert?** The same
   questions repeat every week (is total profit healthy, which line is losing
   money, is the trend turning), so the manager needs to look at the *same*
   view again and again rather than read a new report each time. It is not a
   one-off question, and it is not an alert — the manager also needs the
   trend and category context to judge what to change.

## Step 3 — What Matters

A quick EDA in pandas found the decision-relevant facts:

- The US business makes **$2,297,201 in sales and $286,397 in profit**, a
  **12.5 % margin**; the West ($108k) and East ($92k) lead while the Central
  region ($40k) is the weakest.
- **Heavy discounting loses money.** In the US, line items with no discount run
  at a **29.5 % margin**, 0–20 % discount at 11.9 %, 20–40 % discount at
  **−15.3 %**, and discounts above 40 % at **−77.4 %**.
- **Furniture is the problem category** — high sales but only $18k profit.
  Inside it, **Tables lose $17,725** and Bookcases lose $3,473 in the US.

The app follows this order, top to bottom:

- **Top — three headline numbers (`st.metric` in `st.columns`):** Total sales,
  Total profit, and Profit margin. Within five seconds the manager can answer
  *"is anything wrong right now?"*
- **Middle — two supporting charts:**
  1. **Monthly sales and profit** (trend) — explains *why* a headline moved and
     shows the seasonality (November is the peak, February the trough).
  2. **Profit by sub-category, with losing lines in red** — directly points at
     Tables/Bookcases/Supplies, the lines the manager needs to act on.
- **Filters (sidebar):** a **Market selector** (the manager looks after their
  own market first) and a **date range**. These are the two filters a regional
  manager actually reaches for; no extra sliders.
- **Bottom:** a collapsed "detail by category" table for a manager who wants
  to dig in, kept out of the way by default.

**Two things I chose *not* to show:**

1. **A customer view (segment, customer name, repeat customers).** The snapshot
   has no customer retention or lifetime data over time, so a customer chart
   would not support any operational decision.
2. **A city/country map or geographic breakdown.** The manager acts on
   product lines and discounts, not on hundreds of individual cities; a map
   would look impressive but no action follows from it.

**Things in the data that could mislead, and how the app handles them:**

- **`Postal Code` is missing on ~80 % of rows** (non-US addresses) — the column
  was removed rather than shown with misleading gaps.
- **Discount is not the same as a sale.** The profit chart and the profit
  margin KPI make the negative-margin lines visible, so a manager cannot
  mistake a high-revenue, high-discount line (e.g. Tables) for a good one.
- **It is a static, synthetic snapshot.** The data period and the intended
  production refresh frequency are stated on the page (bottom caption) so no
  one reads the numbers as live.
- **Currency is not labelled in the file.** All dollar figures are treated as
  USD, the conventional reading of this Tableau dataset.

## Step 4 — Refresh Frequency

- **Refresh:** the data would refresh **nightly** from the point-of-sale / ERP
  system, when the day's transactions are settled. Refreshing more often than
  that adds cost without changing a decision, because restock and promotion
  decisions are made **weekly**.
- **Review:** the manager reviews the dashboard **every Monday morning**; the
  data refreshes nightly, but review and refresh are different frequencies.
- **Track over time / trigger action:** the key metric is **profit margin by
  sub-category**. The trigger is **any sub-category running at a negative
  margin for a month** (Tables is already doing this in the snapshot) — that
  should prompt a call to the category/buying team to cut discounts or remove
  the promotion, instead of waiting for the next monthly report.
- **Cost of stale data:** if the dashboard is a week out of date, a
  money-losing discount (like the >40 % discounts that run at −77 % margin)
  can run for an extra week before anyone stops it.

## Step 5 — Run and Deploy

Built with [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
# run locally
uv run streamlit run app.py
```

Deploy: publish this repository to a **public** GitHub repo under your own
account, then in [share.streamlit.io](https://share.streamlit.io/) create a new
app pointing at `app.py`, and under **Advanced settings** set the Python
version to **3.14** (Streamlit Cloud reads `uv.lock` and installs the locked
packages — no `requirements.txt` is needed).
