#!/usr/bin/env python3
"""
BMRCL Ridership Interactive Dashboard & API Server
Compatible with Vercel Serverless Functions (WSGI/app) and local development.
"""

import json
import os
import urllib.parse
from wsgiref.simple_server import make_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, 'data_cache.json')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Load cached analytics (generated from raw datasets)
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
else:
    # Fallback to computing from parquet if data_cache.json is absent
    import pandas as pd
    METRO_LINES = {
        'purple': [
            "Challaghatta", "Kengeri", "Kengeri Bus Terminal", "Pattanagere", "Jnanabharathi",
            "Rajarajeshwari Nagar", "Pantharapalya - Nayandahalli", "Mysore Road", "Deepanjali Nagar",
            "Attiguppe", "Vijayanagar", "Sri Balagangadharanatha Swamiji Station, Hosahalli",
            "Magadi Road", "Krantivira Sangolli Rayanna Railway Station",
            "Nadaprabhu Kempegowda Station, Majestic", "Sir M. Visvesvaraya Stn., Central College",
            "Dr. B. R. Ambedkar Station, Vidhana Soudha", "Cubbon Park", "Mahatma Gandhi Road",
            "Trinity", "Halasuru", "Indiranagar", "Swami Vivekananda Road", "Baiyappanahalli",
            "Benniganahalli", "Krishnarajapura", "Singayyanapalya", "Garudacharpalya", "Hoodi",
            "Seetharampalya", "Kundalahalli", "Nallurahalli", "Sri Sathya Sai Hospital",
            "Pattandur Agrahara", "Kadugodi Tree Park", "Hopefarm Channasandra", "Whitefield (Kadugodi)"
        ],
        'green': [
            "Madavara", "Chikkabidarakallu", "Manjunathanagara", "Nagasandra", "Dasarahalli",
            "Jalahalli", "Peenya Industry", "Peenya", "Goraguntepalya", "Yeshwantpur",
            "Sandal Soap Factory", "Mahalakshmi", "Rajajinagar", "Mahakavi Kuvempu Road",
            "Srirampura", "Mantri Square Sampige Road", "Nadaprabhu Kempegowda Station, Majestic",
            "Chickpete", "Krishna Rajendra Market", "National College", "Lalbagh",
            "South End Circle", "Jayanagar", "Rashtreeya Vidyalaya Road", "Banashankari",
            "Jaya Prakash Nagar", "Yelachenahalli", "Konanakunte Cross", "Doddakallasandra",
            "Vajarahalli", "Thalaghattapura", "Silk Institute"
        ],
        'yellow': [
            "Rashtreeya Vidyalaya Road", "Ragigudda", "Jayadeva Hospital", "BTM Layout",
            "Central Silk Board", "Bommanahalli", "Hongasandra", "Kudlu Gate", "Singasandra",
            "Hosa Road", "Beratena Agrahara", "Electronic City",
            "Infosys Foundation Konappana Agrahara", "Huskur Road", "Biocon Hebbagodi",
            "Delta Electronics Bommasandra"
        ]
    }
    station_to_lines = {}
    for line_name, st_list in METRO_LINES.items():
        for st in st_list:
            if st not in station_to_lines:
                station_to_lines[st] = []
            station_to_lines[st].append(line_name)

    df_entries = pd.read_parquet(os.path.join(DATA_DIR, 'station-hourly.parquet'))
    df_exits = pd.read_parquet(os.path.join(DATA_DIR, 'station-hourly-exits.parquet'))
    df_pairs = pd.read_parquet(os.path.join(DATA_DIR, 'stationpair-hourly-enhanced.parquet'))

    total_entries = int(df_entries['Ridership'].sum())
    total_exits = int(df_exits['Ridership'].sum())
    total_revenue = int(df_pairs['Revenue'].sum())
    unique_stations = sorted(list(set(df_entries['Station'].unique()) | set(df_exits['Station'].unique())))
    date_min = str(min(df_entries['Date'].min(), df_exits['Date'].min()))
    date_max = str(max(df_entries['Date'].max(), df_exits['Date'].max()))
    hourly_labels = [f"{h:02d}:00" for h in range(24)]

    def get_hourly_profile(stations_filter=None):
        ent = df_entries[df_entries['Station'].isin(stations_filter)] if stations_filter else df_entries
        ext = df_exits[df_exits['Station'].isin(stations_filter)] if stations_filter else df_exits
        h_ent = ent.groupby('Hour')['Ridership'].sum().to_dict()
        h_ext = ext.groupby('Hour')['Ridership'].sum().to_dict()
        return {
            'entries': [int(h_ent.get(h, 0)) for h in range(24)],
            'exits': [int(h_ext.get(h, 0)) for h in range(24)]
        }

    line_stats = {}
    for line_name, st_list in METRO_LINES.items():
        ent_sub = df_entries[df_entries['Station'].isin(st_list)]
        ext_sub = df_exits[df_exits['Station'].isin(st_list)]
        ent_sum = int(ent_sub['Ridership'].sum())
        ext_sum = int(ext_sub['Ridership'].sum())
        line_stats[line_name] = {
            'station_count': len(st_list),
            'entries': ent_sum,
            'exits': ext_sum,
            'total': ent_sum + ext_sum
        }

    st_entries = df_entries.groupby('Station')['Ridership'].sum().to_dict()
    st_exits = df_exits.groupby('Station')['Ridership'].sum().to_dict()
    stations_summary = []
    for st in unique_stations:
        ent = int(st_entries.get(st, 0))
        ext = int(st_exits.get(st, 0))
        lines_for_st = station_to_lines.get(st, [])
        stations_summary.append({
            'station': st, 'entries': ent, 'exits': ext, 'total': ent + ext,
            'lines': lines_for_st, 'is_interchange': len(lines_for_st) > 1
        })
    stations_summary.sort(key=lambda x: x['total'], reverse=True)

    top_routes_df = df_pairs.groupby(['Origin Station', 'Destination Station', 'Travelled Stations', 'Fare Slab', 'Fare'], as_index=False).agg({
        'Ridership': 'sum', 'Revenue': 'sum'
    }).sort_values('Ridership', ascending=False)
    top_routes = []
    for r in top_routes_df.head(100).to_dict(orient='records'):
        r['Origin_Lines'] = station_to_lines.get(r['Origin Station'], [])
        r['Dest_Lines'] = station_to_lines.get(r['Destination Station'], [])
        top_routes.append(r)

    station_hourly_lookup = {}
    for st in unique_stations:
        sub_ent = df_entries[df_entries['Station'] == st]
        sub_ext = df_exits[df_exits['Station'] == st]
        h_ent = sub_ent.groupby('Hour')['Ridership'].sum().to_dict()
        h_ext = sub_ext.groupby('Hour')['Ridership'].sum().to_dict()
        station_hourly_lookup[st] = {
            'entries': [int(h_ent.get(h, 0)) for h in range(24)],
            'exits': [int(h_ext.get(h, 0)) for h in range(24)]
        }

    cache = {
        'summary': {
            'total_entries': total_entries, 'total_exits': total_exits, 'total_revenue': total_revenue,
            'station_count': len(unique_stations), 'lines': line_stats, 'date_min': date_min, 'date_max': date_max
        },
        'hourly_labels': hourly_labels,
        'hourly_all': get_hourly_profile(),
        'hourly_purple': get_hourly_profile(METRO_LINES['purple']),
        'hourly_green': get_hourly_profile(METRO_LINES['green']),
        'hourly_yellow': get_hourly_profile(METRO_LINES['yellow']),
        'stations_summary': stations_summary,
        'top_routes': top_routes,
        'metro_lines': METRO_LINES,
        'station_hourly_lookup': station_hourly_lookup
    }

summary = cache['summary']
line_stats = summary['lines']
date_min = summary['date_min']
date_max = summary['date_max']
total_entries = summary['total_entries']
total_exits = summary['total_exits']
total_revenue = summary['total_revenue']
station_count = summary['station_count']

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BMRCL Namma Metro Ridership Analytics | Purple, Green & Yellow Lines</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; color: #f1f5f9; }
    .card-glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-yellow { background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }
    .badge-interchange { background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <header class="border-b border-slate-800 bg-slate-900/90 sticky top-0 z-50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-emerald-600 to-amber-500 flex items-center justify-center font-extrabold text-white text-lg shadow-lg">
          M
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-extrabold text-lg text-white tracking-tight">Namma Metro</span>
            <div class="flex space-x-1">
              <span class="w-2.5 h-2.5 rounded-full bg-purple-500" title="Purple Line"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500" title="Green Line"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-yellow-400" title="Yellow Line"></span>
            </div>
          </div>
          <p class="text-[11px] text-slate-400">Green, Purple & Yellow Line Network Analytics</p>
        </div>
      </div>
      <div class="flex items-center space-x-3 text-xs">
        <span class="hidden sm:inline text-slate-400">RTI Range: <strong class="text-slate-200">""" + f"{date_min} to {date_max}" + """</strong></span>
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span> Active
        </span>
      </div>
    </div>
  </header>

  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div class="card-glass p-5 rounded-2xl relative overflow-hidden border-t-4 border-t-purple-500 hover:scale-[1.01] transition">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <span class="w-3.5 h-3.5 rounded-full bg-purple-500 shadow-[0_0_10px_#a855f7]"></span>
            <h3 class="text-base font-bold text-white">Purple Line</h3>
          </div>
          <span class="text-xs px-2 py-0.5 rounded-full badge-purple font-semibold">""" + f"{line_stats['purple']['station_count']} Stations" + """</span>
        </div>
        <div class="text-2xl font-extrabold text-white">""" + f"{line_stats['purple']['total']:,}" + """</div>
        <div class="text-xs text-purple-300/80 mb-3 font-medium">Total Line Footfall</div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800">
          <div>Entries: <strong class="text-purple-300">""" + f"{line_stats['purple']['entries']:,}" + """</strong></div>
          <div>Exits: <strong class="text-purple-300">""" + f"{line_stats['purple']['exits']:,}" + """</strong></div>
        </div>
        <div class="text-[11px] text-slate-400 mt-2 truncate">Challaghatta ↔ Whitefield (Kadugodi)</div>
      </div>

      <div class="card-glass p-5 rounded-2xl relative overflow-hidden border-t-4 border-t-emerald-500 hover:scale-[1.01] transition">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <span class="w-3.5 h-3.5 rounded-full bg-emerald-500 shadow-[0_0_10px_#22c55e]"></span>
            <h3 class="text-base font-bold text-white">Green Line</h3>
          </div>
          <span class="text-xs px-2 py-0.5 rounded-full badge-green font-semibold">""" + f"{line_stats['green']['station_count']} Stations" + """</span>
        </div>
        <div class="text-2xl font-extrabold text-white">""" + f"{line_stats['green']['total']:,}" + """</div>
        <div class="text-xs text-emerald-300/80 mb-3 font-medium">Total Line Footfall</div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800">
          <div>Entries: <strong class="text-emerald-300">""" + f"{line_stats['green']['entries']:,}" + """</strong></div>
          <div>Exits: <strong class="text-emerald-300">""" + f"{line_stats['green']['exits']:,}" + """</strong></div>
        </div>
        <div class="text-[11px] text-slate-400 mt-2 truncate">Madavara ↔ Silk Institute</div>
      </div>

      <div class="card-glass p-5 rounded-2xl relative overflow-hidden border-t-4 border-t-yellow-400 hover:scale-[1.01] transition">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <span class="w-3.5 h-3.5 rounded-full bg-yellow-400 shadow-[0_0_10px_#facc15]"></span>
            <h3 class="text-base font-bold text-white">Yellow Line</h3>
          </div>
          <span class="text-xs px-2 py-0.5 rounded-full badge-yellow font-semibold">""" + f"{line_stats['yellow']['station_count']} Stations" + """</span>
        </div>
        <div class="text-2xl font-extrabold text-white">""" + f"{line_stats['yellow']['total']:,}" + """</div>
        <div class="text-xs text-yellow-300/80 mb-3 font-medium">Total Line Footfall</div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800">
          <div>Entries: <strong class="text-yellow-300">""" + f"{line_stats['yellow']['entries']:,}" + """</strong></div>
          <div>Exits: <strong class="text-yellow-300">""" + f"{line_stats['yellow']['exits']:,}" + """</strong></div>
        </div>
        <div class="text-[11px] text-slate-400 mt-2 truncate">RV Road ↔ Bommasandra (Electronic City)</div>
      </div>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-2 rounded-xl border border-slate-800">
      <div class="flex items-center space-x-2">
        <span class="text-xs text-slate-400 font-semibold px-2">Line Filter:</span>
        <button onclick="setLineFilter('all')" id="btn-filter-all" class="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-slate-700 text-white transition">All Network</button>
        <button onclick="setLineFilter('purple')" id="btn-filter-purple" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition">🟣 Purple Line</button>
        <button onclick="setLineFilter('green')" id="btn-filter-green" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition">🟢 Green Line</button>
        <button onclick="setLineFilter('yellow')" id="btn-filter-yellow" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition">🟡 Yellow Line</button>
      </div>
      <div class="text-xs text-slate-400 pr-2">
        Interchanges: <span class="badge-interchange px-2 py-0.5 rounded-full font-medium">Majestic (Purple/Green)</span> & <span class="badge-interchange px-2 py-0.5 rounded-full font-medium">RV Road (Green/Yellow)</span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card-glass p-6 rounded-2xl flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-bold text-white">Hourly Ridership by Line</h2>
            <p class="text-xs text-slate-400">Footfall comparison throughout operating hours</p>
          </div>
          <div class="flex items-center space-x-2 text-xs">
            <span class="flex items-center"><span class="w-2.5 h-2.5 rounded-full bg-purple-500 mr-1"></span> Purple</span>
            <span class="flex items-center"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1"></span> Green</span>
            <span class="flex items-center"><span class="w-2.5 h-2.5 rounded-full bg-yellow-400 mr-1"></span> Yellow</span>
          </div>
        </div>
        <div class="relative flex-1 min-h-[300px]">
          <canvas id="linesHourlyChart"></canvas>
        </div>
      </div>

      <div class="card-glass p-6 rounded-2xl flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 id="topStationsTitle" class="text-base font-bold text-white">Top 10 Busiest Stations (All Network)</h2>
            <p class="text-xs text-slate-400">Highest footfall entry/exit stations</p>
          </div>
        </div>
        <div class="relative flex-1 min-h-[300px]">
          <canvas id="topStationsChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card-glass p-6 rounded-2xl space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 class="text-lg font-bold text-white flex items-center">
            <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2"></span> Station Inspector & Line Detail
          </h2>
          <p class="text-xs text-slate-400">Select any metro station to view line membership and peak hour profiles</p>
        </div>
        <div class="w-full sm:w-80">
          <label for="stationSelect" class="block text-xs text-slate-400 mb-1 font-medium">Select Station</label>
          <select id="stationSelect" class="w-full bg-slate-900 border border-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        <div class="space-y-4">
          <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Station Name</div>
            <div id="inspectorStationName" class="text-lg font-bold text-white mt-1">Nadaprabhu Kempegowda Station, Majestic</div>
            <div id="inspectorLineBadges" class="flex flex-wrap gap-1.5 mt-2"></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-purple-400 font-semibold">Total Entries</div>
              <div id="inspectorEntries" class="text-xl font-bold text-slate-100 mt-1">-</div>
            </div>
            <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-emerald-400 font-semibold">Total Exits</div>
              <div id="inspectorExits" class="text-xl font-bold text-slate-100 mt-1">-</div>
            </div>
          </div>
          <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Busiest Hour</div>
            <div id="inspectorPeakHour" class="text-base font-semibold text-amber-400 mt-1">-</div>
          </div>
        </div>
        <div class="lg:col-span-2 relative min-h-[260px]">
          <canvas id="stationInspectorChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card-glass p-6 rounded-2xl space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-white">Top Station Pairs & Commute Routes</h2>
          <p class="text-xs text-slate-400">Origin-destination trips with line tags, fare slabs, and estimated revenues</p>
        </div>
        <input type="text" id="routeSearch" placeholder="Filter station or line..." class="bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-purple-500 w-full sm:w-64">
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="text-slate-400 uppercase bg-slate-900/80 border-b border-slate-800">
            <tr>
              <th class="px-4 py-3">Origin Station</th>
              <th class="px-4 py-3">Destination Station</th>
              <th class="px-3 py-3 text-center">Stations</th>
              <th class="px-3 py-3 text-center">Fare</th>
              <th class="px-4 py-3 text-right">Ridership</th>
              <th class="px-4 py-3 text-right">Est. Revenue</th>
            </tr>
          </thead>
          <tbody id="routesTableBody" class="divide-y divide-slate-800">
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <footer class="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
    BMRCL Namma Metro Analytics • Green Line, Purple Line & Yellow Line
  </footer>

  <script>
    const hourlyLabels = """ + json.dumps(cache['hourly_labels']) + """;
    const hourlyPurple = """ + json.dumps(cache['hourly_purple']) + """;
    const hourlyGreen = """ + json.dumps(cache['hourly_green']) + """;
    const hourlyYellow = """ + json.dumps(cache['hourly_yellow']) + """;
    const stationsSummary = """ + json.dumps(cache['stations_summary']) + """;
    const topRoutes = """ + json.dumps(cache['top_routes']) + """;
    const stationHourlyLookup = """ + json.dumps(cache['station_hourly_lookup']) + """;

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    new Chart(document.getElementById('linesHourlyChart'), {
      type: 'line',
      data: {
        labels: hourlyLabels,
        datasets: [
          {
            label: 'Purple Line',
            data: hourlyPurple.entries.map((v, i) => v + hourlyPurple.exits[i]),
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 2
          },
          {
            label: 'Green Line',
            data: hourlyGreen.entries.map((v, i) => v + hourlyGreen.exits[i]),
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 2
          },
          {
            label: 'Yellow Line',
            data: hourlyYellow.entries.map((v, i) => v + hourlyYellow.exits[i]),
            borderColor: '#facc15',
            backgroundColor: 'rgba(250, 204, 21, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });

    let topStationsChartInstance = null;
    function renderTopStations(stations) {
      const top10 = stations.slice(0, 10);
      if (topStationsChartInstance) topStationsChartInstance.destroy();
      topStationsChartInstance = new Chart(document.getElementById('topStationsChart'), {
        type: 'bar',
        data: {
          labels: top10.map(s => s.station.length > 20 ? s.station.substring(0, 18) + '...' : s.station),
          datasets: [
            { label: 'Entries', data: top10.map(s => s.entries), backgroundColor: '#a855f7', borderRadius: 4 },
            { label: 'Exits', data: top10.map(s => s.exits), backgroundColor: '#22c55e', borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 9 } } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }
    renderTopStations(stationsSummary);

    let currentLineFilter = 'all';
    function setLineFilter(line) {
      currentLineFilter = line;
      ['all', 'purple', 'green', 'yellow'].forEach(l => {
        const btn = document.getElementById('btn-filter-' + l);
        btn.className = l === line 
          ? 'px-3.5 py-1.5 rounded-lg text-xs font-bold bg-slate-700 text-white transition'
          : 'px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition';
      });

      let filteredStations = stationsSummary;
      if (line !== 'all') {
        filteredStations = stationsSummary.filter(s => s.lines.includes(line));
        document.getElementById('topStationsTitle').textContent = `Top 10 Stations (${line.toUpperCase()} LINE)`;
      } else {
        document.getElementById('topStationsTitle').textContent = `Top 10 Busiest Stations (All Network)`;
      }
      renderTopStations(filteredStations);
      populateStationSelect(filteredStations);
      renderRoutes();
    }

    const select = document.getElementById('stationSelect');
    function populateStationSelect(list) {
      select.innerHTML = '';
      list.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.station;
        opt.textContent = `${s.station} (${s.lines.map(l => l.toUpperCase()).join('/')})`;
        select.appendChild(opt);
      });
      if (list.length > 0) {
        loadStationData(list[0].station);
      }
    }

    let inspectorChart = null;
    function loadStationData(stationName) {
      const st = stationsSummary.find(x => x.station === stationName) || { entries: 0, exits: 0, lines: [] };
      document.getElementById('inspectorStationName').textContent = stationName;
      document.getElementById('inspectorEntries').textContent = st.entries.toLocaleString();
      document.getElementById('inspectorExits').textContent = st.exits.toLocaleString();

      const badgeContainer = document.getElementById('inspectorLineBadges');
      badgeContainer.innerHTML = '';
      (st.lines || []).forEach(l => {
        const span = document.createElement('span');
        span.className = `px-2 py-0.5 rounded-full text-[10px] font-bold ${l === 'purple' ? 'badge-purple' : l === 'green' ? 'badge-green' : 'badge-yellow'}`;
        span.textContent = `${l.toUpperCase()} LINE`;
        badgeContainer.appendChild(span);
      });
      if (st.is_interchange) {
        const span = document.createElement('span');
        span.className = 'px-2 py-0.5 rounded-full text-[10px] font-bold badge-interchange';
        span.textContent = 'INTERCHANGE';
        badgeContainer.appendChild(span);
      }

      const data = stationHourlyLookup[stationName] || { entries: new Array(24).fill(0), exits: new Array(24).fill(0) };
      let maxHour = 0, maxVal = -1;
      data.entries.forEach((val, h) => {
        if (val + data.exits[h] > maxVal) {
          maxVal = val + data.exits[h];
          maxHour = h;
        }
      });
      document.getElementById('inspectorPeakHour').textContent = `${maxHour.toString().padStart(2, '0')}:00 - ${(maxHour+1).toString().padStart(2, '0')}:00`;

      if (inspectorChart) inspectorChart.destroy();
      inspectorChart = new Chart(document.getElementById('stationInspectorChart'), {
        type: 'bar',
        data: {
          labels: hourlyLabels,
          datasets: [
            { label: 'Station Entries', data: data.entries, backgroundColor: '#a855f7', borderRadius: 4 },
            { label: 'Station Exits', data: data.exits, backgroundColor: '#22c55e', borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    select.addEventListener('change', (e) => loadStationData(e.target.value));
    populateStationSelect(stationsSummary);

    function renderRoutes() {
      const filter = document.getElementById('routeSearch').value.toLowerCase().trim();
      const tbody = document.getElementById('routesTableBody');
      tbody.innerHTML = '';

      const filtered = topRoutes.filter(r => {
        const matchesText = !filter || 
          r['Origin Station'].toLowerCase().includes(filter) || 
          r['Destination Station'].toLowerCase().includes(filter) ||
          r['Origin_Lines'].some(l => l.includes(filter)) ||
          r['Dest_Lines'].some(l => l.includes(filter));

        const matchesLine = currentLineFilter === 'all' || 
          r['Origin_Lines'].includes(currentLineFilter) || 
          r['Dest_Lines'].includes(currentLineFilter);

        return matchesText && matchesLine;
      });

      filtered.slice(0, 50).forEach(r => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        const origBadges = (r['Origin_Lines'] || []).map(l => `<span class="inline-block w-2 h-2 rounded-full ${l === 'purple' ? 'bg-purple-500' : l === 'green' ? 'bg-emerald-500' : 'bg-yellow-400'} ml-1"></span>`).join('');
        const destBadges = (r['Dest_Lines'] || []).map(l => `<span class="inline-block w-2 h-2 rounded-full ${l === 'purple' ? 'bg-purple-500' : l === 'green' ? 'bg-emerald-500' : 'bg-yellow-400'} ml-1"></span>`).join('');

        tr.innerHTML = `
          <td class="px-4 py-3 font-medium text-slate-100 flex items-center">${r['Origin Station']} ${origBadges}</td>
          <td class="px-4 py-3 text-slate-300">${r['Destination Station']} ${destBadges}</td>
          <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">${r['Travelled Stations']}</span></td>
          <td class="px-3 py-3 text-center text-emerald-400 font-semibold">₹${r['Fare']}</td>
          <td class="px-4 py-3 text-right font-bold text-slate-100">${r['Ridership'].toLocaleString()}</td>
          <td class="px-4 py-3 text-right text-amber-400 font-semibold">₹${r['Revenue'].toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    document.getElementById('routeSearch').addEventListener('input', renderRoutes);
    renderRoutes();
  </script>
</body>
</html>
"""

# Vercel & WSGI Entrypoint Function
def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    query_string = environ.get('QUERY_STRING', '')

    if path == '/' or path == '/index.html':
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Cache-Control', 'public, max-age=3600')
        ])
        return [HTML_PAGE.encode('utf-8')]

    elif path == '/api/summary':
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps(cache['summary']).encode('utf-8')]

    elif path == '/api/station':
        query = urllib.parse.parse_qs(query_string)
        st_name = query.get('name', [''])[0]
        st_data = cache['station_hourly_lookup'].get(st_name, {'entries': [0]*24, 'exits': [0]*24})
        res = {
            'station': st_name,
            'entries': st_data['entries'],
            'exits': st_data['exits']
        }
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps(res).encode('utf-8')]

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

# Top-level exports expected by Vercel Functions runtime:
application = app
handler = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"BMRCL Ridership Analytics Server running at http://localhost:{port}")
    with make_server('0.0.0.0', port, app) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")
