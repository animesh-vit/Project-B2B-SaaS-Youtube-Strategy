# Project B2B SaaS Youtube Strategy Research


<details>
<summary> <b> 📑Table of Contents</b> </summary>

* [Introduction](#introduction)
* [Tools Installed](#tools-installed)
* [Setup Steps](#setup-steps)
* [Issues Encountered](#issues-encountered)
* [Outcome](#outcome)
* [Useful Links](#useful-links)
  
</details>

## Introduction

This repository collects practitioner-led research on **YouTube content strategy for B2B SaaS**. 
This project researches and analyzes how successful B2B SaaS marketers, founders, and content creators use YouTube to generate awareness, build authority, attract qualified leads, and drive business growth.

The **objective** is to identify common patterns, frameworks, and best practices used by industry practitioners who actively create and distribute video content.

### Research Goal

***Primary Question:***
  > What YouTube content strategies consistently help B2B SaaS companies grow?

---
## Selection Criteria
> Experts were selected based on:
>
> * Active involvement in B2B SaaS growth
> * Proven real-world results
> * Strong presence on LinkedIn, YouTube, podcasts, or newsletters
> * Practical experience rather than purely theoretical advice
---

## Repository Structure 
The **YouTube content strategy for B2B SaaS** research set is organized under [`Research/`](Research/):

- [`Research/Sources.md`](Research/Sources.md): the source index with 10 selected experts, profile links, channel links, and short annotations.
- [`Research/Linkedin_Posts/`](Research/Linkedin_Posts/): recent LinkedIn posts collections, organized by expert.
- [`Research/YouTube_Transcripts/`](Research/YouTube_Transcripts/): 15 YouTube transcript files, organized by creator or channel.
- [`Research/Others/`](Research/Others/): supporting analysis, including [`Key Insight.md`](Research/Others/Key%20Insight.md), which summarizes themes across the collected transcripts.

## Experts Selected

| Expert | Why They Were Chosen |
| ---     | ---                 |
| TK Kader | -> SaaS founder, growth advisor, and GTM coach with practical expertise in SaaS growth, positioning, and founder-led execution. <br> -> His content provides valuable insights into how B2B SaaS companies can use educational and founder-driven video content to build authority and generate demand on YouTube.|
| Samu Kovacs | -> Founder of KS Media, focused specifically on helping B2B SaaS companies turn YouTube into a lead generation channel. <br> -> Samu builds modern, revenue-focused B2B YouTube channels. <br> - He actively manages dozens of SaaS accounts to turn educational video content directly into qualified revenue pipeline.|
| Sam Dunning | -> Founder of Breaking B2B, with hands-on work across B2B SEO, YouTube growth, and revenue-focused demand generation. <br> -> Demonstrates how to execute strategies linking YouTube discovery with direct Google SEO capture, ensuring video traffic converts into booked sales pipelines.|
| Tyler Lessard | -> Long-time B2B video strategist and Vidyard executive, useful for understanding video as a sales and marketing channel. <br> -> He is regarded as a leading authority on turning video views into bottom-of-funnel pipeline, mapping YouTube content directly to inbound sales acceleration.|
| Adam Robinson | -> Founder and CEO of Retention.com and RB2B, known for building SaaS momentum through founder-led organic content. <br> -> Chosen for his masterclass in founder personal branding, proving how authentic on-camera storytelling creates a psychological pipeline moat which can be used on YouTube also.|
| Nathan Latka | -> SaaS founder, operator, and podcast host with a large archive of SaaS founder interviews and metrics-driven growth content. <br> -> His data-focused approach provides valuable insights into audience interests, SaaS growth benchmarks, and content strategies that appeal to high-value B2B buyers.|
| Rob Walling | -> TinySeed and MicroConf co-founder with deep experience in bootstrapped SaaS, pricing, positioning, and founder education. <br> - Expert at running highly searchable, educational SaaS YouTube channels that generate compounding ROI without relying on high view counts or vanity metrics.|
| Ross Simmonds | -> Founder of Foundation, chosen for his expertise in SaaS content distribution, SEO, AI search, and "create once, distribute forever" thinking. <br> -> His methodologies help maximize the reach of YouTube content by transforming long-form videos into multiple distribution assets across channels|
| Phil Nottingham | -> Video SEO and demand generation specialist with direct experience in B2B video strategy and organic video growth. <br> -> He provides the foundational structural knowledge for video infrastructure, on-camera presentation positioning, and brand-first media production wwhich can be directly applied to YouTube.|
| Tom Whatley | -> Founder of Grizzle, selected for his practical work in SEO, content strategy, and organic growth for B2B technology companies. <br> -> Tom is a pioneer in AI-native organic growth and technical SEO. <br> -> He bridges the gap between YouTube video transcripts and high-ranking Google/AI search blog structures.|


### Why this combination of experts matters? 

The selected experts cover the complete B2B SaaS YouTube growth ecosystem:

* **YouTube Strategy & Video Marketing:** Phil Nottingham, Tyler Lessard
* **Founder-Led Growth:** Adam Robinson, TK Kader, Rob Walling
* **Content Distribution & SEO:** Ross Simmonds, Samu Kovacs, Tom Whatley
* **SaaS Growth & Demand Generation:** Nathan Latka, Sam Dunning

This combination provides both content expertise and SaaS business context, making the research more practical than studying YouTube tactics alone.

Together, these experts represent complementary perspectives on YouTube content strategy, including video production, SEO, distribution, audience growth, demand generation, founder branding, and SaaS marketing.

---

## Tools Used 
1. Cursor IDE
2. Extensions installed 
     + OpenAI Codex Agent
4. GitHub
5. For Programming & Automation
     + Python
     + youtube-transcript-api
     + yt-dlp
7. For Research 
    + LinkedIn
    + YouTube
    + Manual Research

## Methodology

**1. Topic selection**
+ ***YouTube Content Strategy for B2B SaaS***
    + Reason for selection:
        + Strong overlap between content marketing and SaaS growth.
        + Availability of YouTube, LinkedIn, and podcast content for research.
        + It provides a blueprint to dominate the world's second-largest search engine by turning educational video content into high-intent inbound sales.
          
2. Created GitHub Repository
    > ***Repository Name:*** Project-B2B-SaaS-Youtube-Strategy

3.Local Development Setup in Cursor IDE
+ Cloned the repository locally and opened it in Cursor IDE.
     > git clone https://github.com/animesh-vit/Poject-B2B-SaaS-Youtube-Strategy
     > <br> (In Terminal)
      
5. Used Codex within Cursor IDE to  generate the initial project structure according to the assignment requirements.
+ Repository Structure <br> 

         Research/
         ├── Linkedin_Posts/
         ├── YouTube_Transcripts/
         ├── Others/
               └── Key Insight.md
         └── Sources.md
       
7. Expert Identification & Source Collection
+ Selected & documented leading B2B SaaS marketers, founders, and content creators.
+ Their LinkedIn posts, YouTube videos, podcasts, and articles were collected for analysis.
7. Automated YouTube Transcript Collection
  + Created a lightweight Python script to automatically collect YouTube transcripts using Codex.
    > File: get_transcripts.py [Location: [`Research/Scripts/`](Research/Scripts/)
      + Accepts either a YouTube URL or Video ID
      + Downloads transcripts using youtube-transcript-api
      + Removes timestamps and metadata
      + Cleans and formats transcript text
      + Saves transcripts as structured files
      + Stores output within: [`Research/YouTube_Transcripts/`](Research/YouTube_Transcripts/)
    
8.LinkedIn Content Collection
+ Manually collected relevant LinkedIn posts from selected experts.
+ All posts were organized into a single raw-text file grouped by author in:
    + [`Research/Linkedin_Posts/raw-text-posts`](Research/Linkedin_Posts/raw-text-posts)
  > Format
          >  <br> Source: Author Name
           <br> ## Post 1
      >         <br> ...
      >          <br> ## Post 2
      >          <br>  ...
      >           <br> ## Post 3
      >           <br>  ...       
9. Used Codex within Cursor IDE to analyze collected LinkedIn posts and save them in  [`Research/Linkedin_Posts/`](Research/Linkedin_Posts/).
10. Based on the collected research material, Codex was used to generate structured insights and strategic takeaways. [`Key Insight.md`](Research/Others/Key%20Insight.md)

## Issue
+ Encountered Git identity configuration error during commit.
    + Resolved using:
      > git config --global user.email "your-email@example.com"
      > git config --global user.name "your-github-username"

---

## Outcomes
+ Identified and analyzed leading ***B2B SaaS YouTube and content marketing experts***.
+ Built a structured research repository in GitHub.
+ Automated YouTube transcript collection using Python and youtube-transcript-api.
+ Collected and organized LinkedIn posts and YouTube content for analysis.
+ Generated AI-assisted summaries of expert content using Codex in Cursor IDE.
+ Extracted recurring patterns, frameworks, and best practices across multiple experts.
+ Documented actionable insights on content creation, distribution, audience growth, and demand generation.
+ Demonstrated practical use of AI-assisted research and automation workflows.




