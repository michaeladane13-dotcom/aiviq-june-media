#!/usr/bin/env python3
"""Full natal chart — Swiss Ephemeris. Astro-Seek-grade, every value computed."""
import swisseph as swe
from datetime import datetime
from zoneinfo import ZoneInfo

swe.set_ephe_path("/home/user/aiviq-june-media/chart_work/ephe")

# --- Birth data -----------------------------------------------------------
LAT, LON = 53.4894, -2.0974          # Ashton-under-Lyne, Greater Manchester, UK
local = datetime(1987, 4, 1, 1, 53, tzinfo=ZoneInfo("Europe/London"))
utc = local.astimezone(ZoneInfo("UTC"))
offset = local.utcoffset()
jd = swe.julday(utc.year, utc.month, utc.day,
                utc.hour + utc.minute/60 + utc.second/3600, swe.GREG_CAL)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
GLYPH = dict(zip(SIGNS, "♈♉♊♋♌♍♎♏♐♑♒♓"))
ELEMENT = {s:e for s,e in zip(SIGNS, ["Fire","Earth","Air","Water"]*3)}
MODALITY = {s:m for s,m in zip(SIGNS,
            ["Cardinal","Fixed","Mutable"]*4)}

def fmt(lon):
    lon %= 360
    si = int(lon // 30); d = lon - si*30
    dd = int(d); mm = int((d-dd)*60); ss = int(round((((d-dd)*60)-mm)*60))
    if ss == 60: ss = 0; mm += 1
    if mm == 60: mm = 0; dd += 1
    return f"{dd:2d}°{mm:02d}'{ss:02d}\" {SIGNS[si]} {GLYPH[SIGNS[si]]}", SIGNS[si]

FLG = swe.FLG_MOSEPH | swe.FLG_SPEED          # planets/nodes/lilith: analytic, no files
FLG_AST = swe.FLG_SWIEPH | swe.FLG_SPEED      # chiron/asteroids: need .se1 files

BODIES = [
    ("Sun", swe.SUN, FLG), ("Moon", swe.MOON, FLG), ("Mercury", swe.MERCURY, FLG),
    ("Venus", swe.VENUS, FLG), ("Mars", swe.MARS, FLG), ("Jupiter", swe.JUPITER, FLG),
    ("Saturn", swe.SATURN, FLG), ("Uranus", swe.URANUS, FLG), ("Neptune", swe.NEPTUNE, FLG),
    ("Pluto", swe.PLUTO, FLG),
    ("True Node", swe.TRUE_NODE, FLG), ("Mean Node", swe.MEAN_NODE, FLG),
    ("Lilith (mean)", swe.MEAN_APOG, FLG), ("Lilith (true)", swe.OSCU_APOG, FLG),
    ("Chiron", swe.CHIRON, FLG_AST),
    ("Ceres", swe.CERES, FLG_AST), ("Pallas", swe.PALLAS, FLG_AST),
    ("Juno", swe.JUNO, FLG_AST), ("Vesta", swe.VESTA, FLG_AST),
]

pos = {}      # name -> (lon, speed, declination)
for name, pid, flg in BODIES:
    try:
        xx, _ = swe.calc_ut(jd, pid, flg)
        lon, speed = xx[0], xx[3]
        eq, _ = swe.calc_ut(jd, pid, flg | swe.FLG_EQUATORIAL)
        pos[name] = (lon, speed, eq[1])   # eq[1] = declination
    except Exception as e:
        pos[name] = None
        print(f"  ! {name}: {e}")

# --- Houses (Placidus + Whole Sign) + angles ------------------------------
cusps_P, ascmc = swe.houses_ex(jd, LAT, LON, b'P')
cusps_W, _      = swe.houses_ex(jd, LAT, LON, b'W')
ASC, MC, ARMC, VERTEX = ascmc[0], ascmc[1], ascmc[2], ascmc[3]

def house_of(lon, cusps):
    lon %= 360
    for i in range(12):
        a = cusps[i] % 360; b = cusps[(i+1) % 12] % 360
        if a < b:
            if a <= lon < b: return i+1
        else:
            if lon >= a or lon < b: return i+1
    return 12

# --- Output ---------------------------------------------------------------
print("="*72)
print("  NATAL CHART  —  Swiss Ephemeris 2.10 (Moshier+SwissEph)")
print("="*72)
print(f"  Birth (local) : {local:%Y-%m-%d %H:%M}  {local.tzname()}  (UTC{offset.total_seconds()/3600:+.0f})")
print(f"  Birth (UT)    : {utc:%Y-%m-%d %H:%M} UTC")
print(f"  Place         : Ashton-under-Lyne, UK   {LAT:.4f}N  {abs(LON):.4f}W")
print(f"  Julian Day UT : {jd:.6f}")
print(f"  Day/Night     : ", end="")
sun_h = house_of(pos['Sun'][0], cusps_P)
is_day = sun_h in (7,8,9,10,11,12)
print("DAY chart (Sun above horizon)" if is_day else "NIGHT chart (Sun below horizon)")

print("\n  ANGLES")
for lab, v in [("Ascendant", ASC), ("Midheaven (MC)", MC),
               ("Descendant", ASC+180), ("Imum Coeli (IC)", MC+180),
               ("Vertex", VERTEX)]:
    print(f"    {lab:<16} {fmt(v)[0]}")

print("\n  PLANETS & POINTS" + " "*22 + "house   motion      decl")
order = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus",
         "Neptune","Pluto","Chiron","Ceres","Pallas","Juno","Vesta",
         "True Node","Mean Node","Lilith (mean)","Lilith (true)"]
for n in order:
    if pos.get(n) is None: continue
    lon, sp, dec = pos[n]
    s_pl = house_of(lon, cusps_P)
    rx = "Rx" if sp < 0 else "  "
    txt, _ = fmt(lon)
    print(f"    {n:<14} {txt}   H{s_pl:<2}   {rx} {sp:+7.3f}/d  {dec:+6.2f}°")

print("\n  HOUSE CUSPS                Placidus            Whole Sign")
for i in range(12):
    print(f"    House {i+1:<2}  {fmt(cusps_P[i])[0]:<22}  {fmt(cusps_W[i])[0]}")

# --- Part of Fortune ------------------------------------------------------
Sun, Moon = pos['Sun'][0], pos['Moon'][0]
PoF = (ASC + Moon - Sun) if is_day else (ASC + Sun - Moon)
print(f"\n  Part of Fortune : {fmt(PoF)[0]}   H{house_of(PoF, cusps_P)}  "
      f"({'day' if is_day else 'night'} formula)")

# --- Element / Modality balance (10 planets) ------------------------------
print("\n  ELEMENT / MODALITY BALANCE (10 planets)")
el = {"Fire":0,"Earth":0,"Air":0,"Water":0}
mo = {"Cardinal":0,"Fixed":0,"Mutable":0}
for n in order[:10]:
    _, sign = fmt(pos[n][0])
    el[ELEMENT[sign]] += 1; mo[MODALITY[sign]] += 1
print("    " + "   ".join(f"{k} {v}" for k,v in el.items()))
print("    " + "   ".join(f"{k} {v}" for k,v in mo.items()))

# --- Aspects --------------------------------------------------------------
ASPECTS = [("Conjunction",0,8),("Opposition",180,8),("Trine",120,7),
           ("Square",90,7),("Sextile",60,5),("Quincunx",150,2),
           ("Semisextile",30,1.5),("Semisquare",45,2),("Sesquiquadrate",135,2),
           ("Quintile",72,1.5)]
GL = {"Conjunction":"☌","Opposition":"☍","Trine":"△","Square":"□","Sextile":"✶",
      "Quincunx":"⚻","Semisextile":"⚺","Semisquare":"∠","Sesquiquadrate":"⚼","Quintile":"Q"}
aspect_pts = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus",
              "Neptune","Pluto","Chiron","True Node"]
aspect_pts = [p for p in aspect_pts if pos.get(p)]
# include angles
ang = {"ASC":ASC,"MC":MC}
print("\n  ASPECTS (major + minor, with orb)")
found = []
allpts = [(p, pos[p][0]) for p in aspect_pts] + list(ang.items())
for i in range(len(allpts)):
    for j in range(i+1, len(allpts)):
        n1,l1 = allpts[i]; n2,l2 = allpts[j]
        diff = abs((l1-l2) % 360)
        if diff > 180: diff = 360 - diff
        for an, ang_deg, orb in ASPECTS:
            d = abs(diff - ang_deg)
            if d <= orb:
                found.append((d, n1, an, n2))
                break
for d, n1, an, n2 in sorted(found):
    print(f"    {n1:<11} {GL[an]} {an:<14} {n2:<11}  orb {d:4.2f}°")

# --- Essential dignities (traditional rulerships) -------------------------
RULER = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
         "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
         "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mercury":"Virgo","Venus":"Pisces",
         "Mars":"Capricorn","Jupiter":"Cancer","Saturn":"Libra"}
DETRI = {"Mars":["Taurus","Libra"],"Venus":["Aries","Scorpio"],"Mercury":["Sagittarius","Pisces"],
         "Moon":["Capricorn"],"Sun":["Aquarius"],"Jupiter":["Gemini","Virgo"],
         "Saturn":["Cancer","Leo"]}
print("\n  ESSENTIAL DIGNITIES (traditional)")
for n in order[:7]:
    _, sign = fmt(pos[n][0])
    tags = []
    if RULER[sign] == n: tags.append("Rulership")
    if EXALT.get(n) == sign: tags.append("Exaltation")
    if sign in DETRI.get(n, []): tags.append("Detriment")
    if EXALT.get(n) and SIGNS[(SIGNS.index(EXALT[n])+6)%12] == sign: tags.append("Fall")
    print(f"    {n:<9} in {sign:<11} {'  '.join(tags) if tags else 'peregrine'}")
print("="*72)
