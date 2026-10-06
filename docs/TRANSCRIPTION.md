# Transcribing CQ's WAZ Zone Definitions

`src/cq_zones_mcp/data/facts/cq_zones.json` holds the facts of CQ's **WAZ Zone Definitions**
(<https://cqww.com/cq_waz_list.htm>, "Updated and correct as of April 1, 2018"). The page itself is not
included (it is CQ's); `data/SOURCE.json` records its URL and SHA-256. CQ's page is prose, so its facts were copied in
by hand once and reviewed. This file records how the copy was read: every judgement call, and every
slip in CQ's text that was kept as published. Where a record needed a word of explanation, it carries a
`transcription_note`.

**40 zones, 439 covers.** Checked when transcribed:
- every zone name, prefix and boundary appears word for word in that zone's paragraph of the page;
- every prefix CQ sets in bold is accounted for by a cover;
- every DXCC and subdivision code is one of ADIF 3.1.7's.

## How a zone's text becomes covers

- One cover per entity or subdivision CQ names, in CQ's order. `prefix` is CQ's prefix as printed,
  `dxcc` and `pas` are ADIF's codes, and `boundary` is CQ's own wording for a partial area.
- `pas` is set only where CQ names a state, province or territory ("the W7 states of Arizona, Idaho,
  …" gives one cover per state). A US call district alone (W6, W0, W9, W5, W1, W2, W3) has `pas` null.
  "W8 (except West Virginia)" is prefix W8 with boundary "except West Virginia".
- Bold runs that list several prefixes ("4U1UN, CY9", "W0, W9, W8", the BY lists, the Zone 16 Russian
  run) are one cover per prefix. "UA2,F,K, RA2,UB2-UI2" and the "UA8,9 (…)" and "UA0 (…)" strings stay
  single covers, as printed.
- A prefix CQ repeats for different areas (FO, HK0, PY0, CE0, VP8, JD1, VU, 3Y, VK9, VK0) is mapped by
  the area CQ names.
- One prefix covering more than one ADIF entity gets one cover per entity: 9M (299, 46), E5 (191,
  234), FO in Zone 32 (175 with "but NOT Marquesas and Clipperton", and 508), VP6 (172, 513), 3D2
  (176, 460, 489).
- Current ADIF codes are used where CQ's prefix names a current entity: DL 230, E4 510, D6 411.
- Prefix characters are kept exactly, including the non-breaking hyphen (U+2011) CQ uses in BY3G‑L,
  BY9G‑L, BY9M‑R, BY9S‑Z, BY3A‑F, BY3M‑R, BY9A‑F, FT‑W and FT‑Z. Anything matching prefixes should
  treat U+2011 as a hyphen.

## Judgement calls

1. **Zone 1:** "west of 102 degrees (Includes the islands of …)" is the boundary of both VE8 (NT) and
   VY0 (NU); the sentence governs both.
2. **Zone 2:** the Nunavut text east of 102 degrees names no prefix: prefix null, pas NU, CQ's full
   wording as boundary.
3. **Zone 4:** the VY0 Hudson Bay islands are pas NU, as Zone 2 places Nunavut.
4. **VO2 (Labrador) and VO1 (Newfoundland)** are both pas NL, with boundary "Labrador" or
   "Newfoundland".
5. **Pelagie and Pantelleria (Zone 33)** are Italy (248), with CQ's wording as boundary.
6. **Chinese provinces and Australian states** CQ names use ADIF's codes (NM, GS, NX, QH, TJ, HE, SX,
   SN; WA, NT, ACT, NSW, VIC, QLD, SA, TAS).
7. **Antarctica:** each "some Antarctic stations (See Notes Below)" is a cover with prefix null, dxcc
   13 (ANTARCTICA) and that zone's wording. The Notes say KC4AAA and KC4USN count for any one of zones
   12, 13, 29, 30, 32, 38 and 39, so those zones also carry KC4AAA and KC4USN covers, with the Notes
   sentence as boundary and source "Zone N; Notes". These two are callsigns, not prefixes.
8. **Paracel Islands (Zone 26):** not a DXCC entity, and CQ's footnote gives no prefix: one cover with
   prefix and dxcc null. The footnote is the record's `transcription_note`.

## Doubtful, mapped and flagged

- **Zone 8, KP5 "(Navassa Is.)":** KP1 is already Navassa; KP5 is Desecheo. Mapped by prefix to 43
  (Desecheo).
- **Zone 16, "UA2(except for RA2 and UA2-UI2)":** UA2 is Kaliningrad, which CQ places in Zone 15, so no
  remainder is evident. Mapped by prefix to 126.
- **Zone 16, a bare "UA9" before "UA9 (S,T,W)":** mapped to 15 (Asiatic Russia). It contradicts Zones
  17–18 and is probably a stray.
- **Zone 31, KH5K Kingman Reef:** 134, which ADIF lists as deleted (CQ's 2018 list still names it).

## Slips in CQ's text, kept as published

Zone 2 "King William. Prince of Wales"; Zone 8 "KP2 Virgin Islands)"; Zone 11 "(Fernando de Noronha,";
Zone 14 "El" for EI; Zone 16 "UA3." (recorded as UA3); Zone 17 "J. K"; Zone 18 "UAO" (letter O) with an
unclosed parenthesis; Zone 31 "Johnson Is." and "Bananba"; Zone 32 "FK New Caledonia … Is.)"; Zone 33
IG9 listed twice; Zone 39 "Mautitius".

Not assigned to any zone by CQ: the Russian district letters UA8/9 E and UA0 E, G, M, N, P; and the
Republic of Kosovo (Z6, 522), added to DXCC in 2018.

## Cross-checks (CQ's text wins)

These are tested in `tests/test_crosscheck.py` (AD1C and ARRL fetched live); a new disagreement fails the tests.

- **ADIF 3.1.7's subdivision zones:** ADIF gives North Carolina (NC) zone 04; CQ puts it in Zone 5.
  ADIF gives Nunavut (NU) zone 02 only; CQ also places parts of Nunavut in Zones 1 and 4.
- **ARRL's DXCC list:** Yemen (492) zone 21 only; CQ puts Socotra and Abd al Kuri in Zone 37.
- **AD1C's cty.dat:** Yemen zone 21; KC4AAA fixed to 39; several Russian districts default to zone 17
  where CQ gives 18, 19 or 23 (a gap in cty.dat's prefix overrides, not a reassignment).
