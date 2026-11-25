# Ezhalha V2 — design direction

Approved primary color: `#125065` (owner confirmed in this session). This supersedes the previous teal palette for this redesign. The original brief is the authoritative visual direction.

## Visual references and decisions

Apple's product presentation informs whitespace, typography hierarchy, real product imagery, and short sections. No Apple assets or layout are copied. Official Salla and Zid sites inform platform-specific navigation; the agency experience emphasizes actual implementation work, package scope, and a clear handoff.

The visual board combines deep blue-green, white, a soft blue-green canvas, restrained champagne accents, large Arabic headings, fine dividers, and real store screenshots. The hero is a small exhibition of actual storefronts. Services are concise editorial rows; selected work uses generous image areas; prices are three comparable tiers; process is a sequence; FAQs use native disclosure elements.

## Typography

IBM Plex Sans Arabic is selected for contemporary Arabic headings, connected letterforms, and readable numerals. Noto Sans Arabic is the fallback, followed by system Arabic fonts. Alexandria's geometric construction was considered but is less suited to long service and knowledge articles in this direction. Use 400/500 for body and 600/700 for emphasis, no synthetic tracking on Arabic. Google Fonts' IBM Plex Sans Arabic family is served with `display=swap`; local font hosting remains preferable when official font bytes can be fetched and the license retained.

## Information architecture

Homepage: promise and real work → platform links → selected projects → service scope → package comparison → working process → guided advisor → FAQ → contact. Pricing and portfolio remain reachable directly from the header. Existing canonical paths, service pages, articles, and redirects stay intact. Core marketing content is static HTML, including navigation and package facts.

## Components and tokens

`css/ezhalha-v2.css` owns the new palette, spacing, typography, border radii, layout width, focus styles, and responsive behavior. The new homepage is built directly in HTML. Existing inner pages receive the same shared design layer while retaining their content and URLs. Interactive logic is in `js/ezhalha-v2.js`; the existing advisor, booking, and portfolio logic remain separate.

## Asset protection

Original image files are retained. Homepage thumbnails are new derivatives of real portfolio screenshots. A scoped backup precedes rewriting the homepage and shared shell. Importing the owner’s newer logo was attempted, but the transfer could not resolve DNS; the existing local wordmark remains available pending successful import.
