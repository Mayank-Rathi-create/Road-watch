"""
Municipal Authority Directory & Nearest Office Locator for Civic-Connect.

Provides geolocation-based discovery of the nearest municipal corporation /
urban local body (ULB) office and their official complaint/grievance emails.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points in kilometers.
    """
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


# Curated directory of Municipal Corporations and Urban Local Bodies
# Covers major cities, state capitals, and industrial hubs across regions.
MUNICIPAL_AUTHORITIES: List[Dict[str, Any]] = [
    # Karnataka
    {
        "name": "Bruhat Bengaluru Mahanagara Palike (BBMP)",
        "short": "BBMP",
        "city": "Bengaluru",
        "state": "Karnataka",
        "lat": 12.9716,
        "lng": 77.5946,
        "email": "complaints@bbmp.gov.in",
        "alt_emails": ["contactusbbmp@gmail.com", "commissioner@bbmp.gov.in"],
        "helpline": "1533 / 080-22660000",
        "portal": "https://bbmp.gov.in",
        "aliases": ["bengaluru", "bangalore", "bbmp", "koramangala", "indiranagar", "whitefield", "jayanagar", "yelahanka"],
    },
    {
        "name": "Mysuru City Corporation (MCC)",
        "short": "MCC Mysuru",
        "city": "Mysuru",
        "state": "Karnataka",
        "lat": 12.2958,
        "lng": 76.6394,
        "email": "commissioner@mysurucitycorporation.gov.in",
        "alt_emails": ["itstaff_mcc@yahoo.com"],
        "helpline": "0821-2440890",
        "portal": "https://mysurucitycorporation.gov.in",
        "aliases": ["mysuru", "mysore"],
    },
    {
        "name": "Mangaluru City Corporation (MCC)",
        "short": "MCC Mangaluru",
        "city": "Mangaluru",
        "state": "Karnataka",
        "lat": 12.9141,
        "lng": 74.8560,
        "email": "commissioner.mcc@gmail.com",
        "alt_emails": ["mccitcell@gmail.com"],
        "helpline": "0824-2220306",
        "portal": "https://mangalurucity.mrc.gov.in",
        "aliases": ["mangaluru", "mangalore", "dakshina kannada"],
    },
    {
        "name": "Hubballi-Dharwad Municipal Corporation (HDMC)",
        "short": "HDMC",
        "city": "Hubballi",
        "state": "Karnataka",
        "lat": 15.3647,
        "lng": 75.1240,
        "email": "commissioner.hdmc@gmail.com",
        "alt_emails": ["itcellhdmc@gmail.com"],
        "helpline": "0836-2213888",
        "portal": "https://hdmc.mrc.gov.in",
        "aliases": ["hubballi", "hubli", "dharwad", "hdmc"],
    },
    {
        "name": "City Corporation Belagavi",
        "short": "BCC",
        "city": "Belagavi",
        "state": "Karnataka",
        "lat": 15.8497,
        "lng": 74.4977,
        "email": "commbcc@yahoo.in",
        "alt_emails": ["itstaff_bcc@yahoo.in"],
        "helpline": "0831-2405337",
        "portal": "https://belagavicity.mrc.gov.in",
        "aliases": ["belagavi", "belgaum"],
    },

    # Maharashtra
    {
        "name": "Brihanmumbai Municipal Corporation (BMC)",
        "short": "BMC",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 18.9400,
        "lng": 72.8353,
        "email": "complaints@mcgm.gov.in",
        "alt_emails": ["mc@mcgm.gov.in", "portalhelpdesk.it@mcgm.gov.in"],
        "helpline": "1916 / 022-22694725",
        "portal": "https://www.mcgm.gov.in",
        "aliases": ["mumbai", "bombay", "mcgm", "bandra", "andheri", "borivali", "colaba", "dadar"],
    },
    {
        "name": "Pune Municipal Corporation (PMC)",
        "short": "PMC",
        "city": "Pune",
        "state": "Maharashtra",
        "lat": 18.5204,
        "lng": 73.8567,
        "email": "complaint@punecorporation.org",
        "alt_emails": ["feedback@punecorporation.org", "info@punecorporation.org"],
        "helpline": "1800-1030-222 / 020-25501000",
        "portal": "https://pmc.gov.in",
        "aliases": ["pune", "pmc", "shivajinagar", "kothrud", "hadapsar", "viman nagar"],
    },
    {
        "name": "Pimpri Chinchwad Municipal Corporation (PCMC)",
        "short": "PCMC",
        "city": "Pimpri-Chinchwad",
        "state": "Maharashtra",
        "lat": 18.6298,
        "lng": 73.7997,
        "email": "commissioner@pcmcindia.gov.in",
        "alt_emails": ["sarathi@pcmcindia.gov.in"],
        "helpline": "020-67333333 / 8888006666",
        "portal": "https://www.pcmcindia.gov.in",
        "aliases": ["pimpri", "chinchwad", "pcmc", "nigdi", "bhosari", "hinjewadi"],
    },
    {
        "name": "Thane Municipal Corporation (TMC)",
        "short": "TMC",
        "city": "Thane",
        "state": "Maharashtra",
        "lat": 19.2183,
        "lng": 72.9781,
        "email": "feedback@thanecity.gov.in",
        "alt_emails": ["complaint@thanecity.gov.in"],
        "helpline": "1800-222-108",
        "portal": "https://thanecity.gov.in",
        "aliases": ["thane", "tmc", "ghodbunder"],
    },
    {
        "name": "Navi Mumbai Municipal Corporation (NMMC)",
        "short": "NMMC",
        "city": "Navi Mumbai",
        "state": "Maharashtra",
        "lat": 19.0330,
        "lng": 73.0297,
        "email": "commissioner@nmmc.gov.in",
        "alt_emails": ["info@nmmconline.com"],
        "helpline": "022-27567070 / 1800-222-309",
        "portal": "https://www.nmmc.gov.in",
        "aliases": ["navi mumbai", "vashi", "nerul", "belapur", "nmmc"],
    },
    {
        "name": "Nagpur Municipal Corporation (NMC)",
        "short": "NMC Nagpur",
        "city": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.1458,
        "lng": 79.0882,
        "email": "nmc@nagpurmunicipal.com",
        "alt_emails": ["contact@nmcnagpur.gov.in"],
        "helpline": "0712-2567035",
        "portal": "https://www.nmcnagpur.gov.in",
        "aliases": ["nagpur", "nmc"],
    },
    {
        "name": "Nashik Municipal Corporation (NMC)",
        "short": "NMC Nashik",
        "city": "Nashik",
        "state": "Maharashtra",
        "lat": 19.9975,
        "lng": 73.7898,
        "email": "feedback@nashikcorporation.in",
        "alt_emails": ["commissioner@nashikcorporation.in"],
        "helpline": "0253-2575631",
        "portal": "https://nashikcorporation.in",
        "aliases": ["nashik", "nasik"],
    },

    # Delhi NCR
    {
        "name": "Municipal Corporation of Delhi (MCD)",
        "short": "MCD",
        "city": "Delhi",
        "state": "Delhi",
        "lat": 28.6139,
        "lng": 77.2090,
        "email": "mcd-ithelpdesk@mcd.org.in",
        "alt_emails": ["commissioner-mcd@mcd.org.in"],
        "helpline": "155305 / 011-23225000",
        "portal": "https://mcdonline.nic.in",
        "aliases": ["delhi", "new delhi", "north delhi", "south delhi", "east delhi", "mcd", "rohini", "dwarka"],
    },
    {
        "name": "New Delhi Municipal Council (NDMC)",
        "short": "NDMC",
        "city": "New Delhi",
        "state": "Delhi",
        "lat": 28.6289,
        "lng": 77.2065,
        "email": "complaint@ndmc.gov.in",
        "alt_emails": ["chairman@ndmc.gov.in"],
        "helpline": "1533 / 011-23360118",
        "portal": "https://online.ndmc.gov.in",
        "aliases": ["connaught place", "chanakyapuri", "lutyens", "ndmc"],
    },
    {
        "name": "Municipal Corporation of Gurugram (MCG)",
        "short": "MCG",
        "city": "Gurugram",
        "state": "Haryana",
        "lat": 28.4595,
        "lng": 77.0266,
        "email": "commissioner@mcg.gov.in",
        "alt_emails": ["complaint@mcg.gov.in"],
        "helpline": "1800-180-1817",
        "portal": "https://www.mcg.gov.in",
        "aliases": ["gurugram", "gurgaon", "mcg", "cyber city", "sohna"],
    },
    {
        "name": "NOIDA Authority",
        "short": "NOIDA",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "lat": 28.5355,
        "lng": 77.3910,
        "email": "noida@noidaauthorityonline.com",
        "alt_emails": ["ceo@noidaauthorityonline.com"],
        "helpline": "0120-2422201 / 0120-2425025",
        "portal": "https://noidaauthorityonline.in",
        "aliases": ["noida", "gautam buddha nagar", "sector 62", "sector 18"],
    },
    {
        "name": "Greater Noida Industrial Development Authority (GNIDA)",
        "short": "GNIDA",
        "city": "Greater Noida",
        "state": "Uttar Pradesh",
        "lat": 28.4744,
        "lng": 77.5040,
        "email": "authority@gnida.in",
        "alt_emails": ["ceo@gnida.in"],
        "helpline": "0120-2326335",
        "portal": "https://www.greaternoidaauthority.in",
        "aliases": ["greater noida", "gnida"],
    },
    {
        "name": "Ghaziabad Nagar Nigam (GNN)",
        "short": "GNN",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "lat": 28.6692,
        "lng": 77.4538,
        "email": "gmc@onlinegnn.com",
        "alt_emails": ["nagarnigamghaziabad@gmail.com"],
        "helpline": "1800-180-3012",
        "portal": "https://onlinegnn.com",
        "aliases": ["ghaziabad", "gnn", "indirapuram", "vaishali"],
    },
    {
        "name": "Municipal Corporation Faridabad (MCF)",
        "short": "MCF",
        "city": "Faridabad",
        "state": "Haryana",
        "lat": 28.4089,
        "lng": 77.3178,
        "email": "mcf.faridabad@gmail.com",
        "alt_emails": ["commissioner@mcf.gov.in"],
        "helpline": "0129-2411664",
        "portal": "https://www.mcfbd.com",
        "aliases": ["faridabad", "mcf"],
    },

    # Tamil Nadu
    {
        "name": "Greater Chennai Corporation (GCC)",
        "short": "GCC",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lng": 80.2707,
        "email": "grievance@chennaicorporation.gov.in",
        "alt_emails": ["commissioner@chennaicorporation.gov.in", "gcc1913@gmail.com"],
        "helpline": "1913 / 044-25619206",
        "portal": "https://chennaicorporation.gov.in",
        "aliases": ["chennai", "madras", "gcc", "adyar", "t nagar", "velachery", "anna nagar"],
    },
    {
        "name": "Coimbatore City Municipal Corporation (CCMC)",
        "short": "CCMC",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "lat": 11.0168,
        "lng": 76.9558,
        "email": "commr.coimbatore@tn.gov.in",
        "alt_emails": ["coimbatorecorporation@gmail.com"],
        "helpline": "0422-2302323 / 1800-425-4243",
        "portal": "https://www.ccmc.gov.in",
        "aliases": ["coimbatore", "ccmc"],
    },
    {
        "name": "Madurai Corporation",
        "short": "MCC Madurai",
        "city": "Madurai",
        "state": "Tamil Nadu",
        "lat": 9.9252,
        "lng": 78.1198,
        "email": "commr.madurai@tn.gov.in",
        "alt_emails": ["maduraicorporation@gmail.com"],
        "helpline": "0452-2533246",
        "portal": "https://www.maduraicorporation.co.in",
        "aliases": ["madurai"],
    },
    {
        "name": "Tiruchirappalli City Corporation",
        "short": "TCC",
        "city": "Tiruchirappalli",
        "state": "Tamil Nadu",
        "lat": 10.7905,
        "lng": 78.7047,
        "email": "commr.trichy@tn.gov.in",
        "alt_emails": ["trichycorporation@gmail.com"],
        "helpline": "0431-2415381",
        "portal": "https://trichycorporation.gov.in",
        "aliases": ["trichy", "tiruchirappalli"],
    },

    # Telangana & Andhra Pradesh
    {
        "name": "Greater Hyderabad Municipal Corporation (GHMC)",
        "short": "GHMC",
        "city": "Hyderabad",
        "state": "Telangana",
        "lat": 17.4065,
        "lng": 78.4772,
        "email": "complaints.ghmc@gmail.com",
        "alt_emails": ["commissioner-ghmc@gov.in"],
        "helpline": "040-21111111 / 155304",
        "portal": "https://www.ghmc.gov.in",
        "aliases": ["hyderabad", "secunderabad", "ghmc", "cyberabad", "gachibowli", "hitec city", "madhapur"],
    },
    {
        "name": "Greater Warangal Municipal Corporation (GWMC)",
        "short": "GWMC",
        "city": "Warangal",
        "state": "Telangana",
        "lat": 17.9689,
        "lng": 79.5941,
        "email": "commissioner_gwmch@yahoo.co.in",
        "alt_emails": ["gwmcward@gmail.com"],
        "helpline": "1800-425-1980",
        "portal": "https://gwmc.gov.in",
        "aliases": ["warangal", "hanamkonda", "kazipet"],
    },
    {
        "name": "Greater Visakhapatnam Municipal Corporation (GVMC)",
        "short": "GVMC",
        "city": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "lat": 17.6868,
        "lng": 83.2185,
        "email": "commissioner_gvmc@yahoo.co.in",
        "alt_emails": ["grievance.gvmc@gmail.com"],
        "helpline": "1800-425-00009 / 0891-2755555",
        "portal": "https://www.gvmc.gov.in",
        "aliases": ["visakhapatnam", "vizag", "gvmc"],
    },
    {
        "name": "Vijayawada Municipal Corporation (VMC)",
        "short": "VMC Vijayawada",
        "city": "Vijayawada",
        "state": "Andhra Pradesh",
        "lat": 16.5062,
        "lng": 80.6480,
        "email": "ourvmc@yahoo.com",
        "alt_emails": ["commissioner@ourvmc.org"],
        "helpline": "0866-2422400 / 0866-2424172",
        "portal": "https://www.ourvmc.org",
        "aliases": ["vijayawada", "vmc"],
    },
    {
        "name": "Guntur Municipal Corporation (GMC)",
        "short": "GMC Guntur",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "lat": 16.3067,
        "lng": 80.4365,
        "email": "commissioner@gunturcorporation.org",
        "alt_emails": ["gunturcorporation@gmail.com"],
        "helpline": "0863-2224202",
        "portal": "https://gunturcorporation.org",
        "aliases": ["guntur"],
    },

    # West Bengal & East
    {
        "name": "Kolkata Municipal Corporation (KMC)",
        "short": "KMC",
        "city": "Kolkata",
        "state": "West Bengal",
        "lat": 22.5626,
        "lng": 88.3510,
        "email": "feedback@kmcgov.in",
        "alt_emails": ["mc@kmcgov.in", "dg_it@kmcgov.in"],
        "helpline": "155300 / 033-22861212",
        "portal": "https://www.kmcgov.in",
        "aliases": ["kolkata", "calcutta", "kmc", "salt lake", "howrah"],
    },
    {
        "name": "Bhubaneswar Municipal Corporation (BMC)",
        "short": "BMC Bhubaneswar",
        "city": "Bhubaneswar",
        "state": "Odisha",
        "lat": 20.2961,
        "lng": 85.8245,
        "email": "info@bmc.gov.in",
        "alt_emails": ["commissioner@bmc.gov.in"],
        "helpline": "1800-345-0061 / 0674-2431253",
        "portal": "https://www.bmc.gov.in",
        "aliases": ["bhubaneswar", "bmc odisha"],
    },
    {
        "name": "Cuttack Municipal Corporation (CMC)",
        "short": "CMC Cuttack",
        "city": "Cuttack",
        "state": "Odisha",
        "lat": 20.4625,
        "lng": 85.8830,
        "email": "cmc_cuttack@rediffmail.com",
        "alt_emails": ["commissioner@cmccuttack.gov.in"],
        "helpline": "0671-2312301",
        "portal": "https://cmccuttack.gov.in",
        "aliases": ["cuttack"],
    },
    {
        "name": "Ranchi Municipal Corporation (RMC)",
        "short": "RMC Ranchi",
        "city": "Ranchi",
        "state": "Jharkhand",
        "lat": 23.3441,
        "lng": 85.3096,
        "email": "support@rmcranchi.org",
        "alt_emails": ["commissioner@rmcranchi.org"],
        "helpline": "1800-890-4115 / 0651-2200011",
        "portal": "https://www.rmcranchi.org",
        "aliases": ["ranchi", "rmc"],
    },
    {
        "name": "Patna Municipal Corporation (PMC)",
        "short": "PMC Patna",
        "city": "Patna",
        "state": "Bihar",
        "lat": 25.5941,
        "lng": 85.1376,
        "email": "pmcpatna@gmail.com",
        "alt_emails": ["commissioner-pmc-bih@nic.in"],
        "helpline": "155304 / 0612-2223791",
        "portal": "https://www.pmc.bihar.gov.in",
        "aliases": ["patna", "pmc bihar"],
    },
    {
        "name": "Guwahati Municipal Corporation (GMC)",
        "short": "GMC Guwahati",
        "city": "Guwahati",
        "state": "Assam",
        "lat": 26.1445,
        "lng": 91.7362,
        "email": "guwahaticommissioner@gmail.com",
        "alt_emails": ["gmcassam@gmail.com"],
        "helpline": "0361-2540525 / 8811007000",
        "portal": "https://gmc.assam.gov.in",
        "aliases": ["guwahati", "kamrup", "dispur"],
    },

    # Gujarat
    {
        "name": "Amdavad Municipal Corporation (AMC)",
        "short": "AMC",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "lat": 23.0225,
        "lng": 72.5714,
        "email": "info@ahmedabadcity.gov.in",
        "alt_emails": ["commissioner@ahmedabadcity.gov.in"],
        "helpline": "155303 / 079-25391811",
        "portal": "https://ahmedabadcity.gov.in",
        "aliases": ["ahmedabad", "amdavad", "amc"],
    },
    {
        "name": "Surat Municipal Corporation (SMC)",
        "short": "SMC Surat",
        "city": "Surat",
        "state": "Gujarat",
        "lat": 21.1702,
        "lng": 72.8311,
        "email": "commissioner@suratmunicipal.gov.in",
        "alt_emails": ["complaint@suratmunicipal.gov.in"],
        "helpline": "0261-2423751 / 1800-123-8000",
        "portal": "https://www.suratmunicipal.gov.in",
        "aliases": ["surat", "smc"],
    },
    {
        "name": "Vadodara Municipal Corporation (VMC)",
        "short": "VMC Vadodara",
        "city": "Vadodara",
        "state": "Gujarat",
        "lat": 22.3072,
        "lng": 73.1812,
        "email": "commissioner@vmc.gov.in",
        "alt_emails": ["complaints@vmc.gov.in"],
        "helpline": "1800-233-0265 / 0265-2433116",
        "portal": "https://vmc.gov.in",
        "aliases": ["vadodara", "baroda", "vmc"],
    },
    {
        "name": "Rajkot Municipal Corporation (RMC)",
        "short": "RMC Rajkot",
        "city": "Rajkot",
        "state": "Gujarat",
        "lat": 22.3039,
        "lng": 70.8022,
        "email": "mc_rmc@rmc.gov.in",
        "alt_emails": ["info@rmc.gov.in"],
        "helpline": "0281-2224258",
        "portal": "https://www.rmc.gov.in",
        "aliases": ["rajkot", "rmc"],
    },

    # Rajasthan
    {
        "name": "Jaipur Greater Municipal Corporation",
        "short": "JMC Jaipur",
        "city": "Jaipur",
        "state": "Rajasthan",
        "lat": 26.9124,
        "lng": 75.7873,
        "email": "helpline@jaipurmc.org",
        "alt_emails": ["comm.jmc@rajasthan.gov.in"],
        "helpline": "0141-2742900 / 0141-2742823",
        "portal": "https://jaipurmc.org",
        "aliases": ["jaipur", "pink city", "jmc"],
    },
    {
        "name": "Jodhpur Nagar Nigam",
        "short": "JNN",
        "city": "Jodhpur",
        "state": "Rajasthan",
        "lat": 26.2389,
        "lng": 73.0243,
        "email": "nnjodhpur@gmail.com",
        "alt_emails": ["comm.nnjodhpur@rajasthan.gov.in"],
        "helpline": "0291-2651496",
        "portal": "https://urban.rajasthan.gov.in/jodhpur",
        "aliases": ["jodhpur"],
    },
    {
        "name": "Kota Nagar Nigam",
        "short": "KNN Kota",
        "city": "Kota",
        "state": "Rajasthan",
        "lat": 25.2138,
        "lng": 75.8648,
        "email": "nnkhelpdesk@gmail.com",
        "alt_emails": ["comm.kotamc@rajasthan.gov.in"],
        "helpline": "0744-2502244",
        "portal": "https://urban.rajasthan.gov.in/kota",
        "aliases": ["kota"],
    },

    # Uttar Pradesh
    {
        "name": "Lucknow Municipal Corporation (LMC)",
        "short": "LMC Lucknow",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "lat": 26.8467,
        "lng": 80.9462,
        "email": "nnlko@nic.in",
        "alt_emails": ["commissionerlmc@gmail.com"],
        "helpline": "1533 / 0522-2615195",
        "portal": "https://lmc.up.nic.in",
        "aliases": ["lucknow", "lmc", "hazratganj", "gomti nagar"],
    },
    {
        "name": "Kanpur Nagar Nigam (KNN)",
        "short": "KNN Kanpur",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "lat": 26.4499,
        "lng": 80.3319,
        "email": "knmkanpur@gmail.com",
        "alt_emails": ["commissioner@kmc.up.nic.in"],
        "helpline": "0512-2541258 / 1800-180-5124",
        "portal": "https://kmc.up.nic.in",
        "aliases": ["kanpur", "knn"],
    },
    {
        "name": "Varanasi Nagar Nigam (VNN)",
        "short": "VNN Varanasi",
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "lat": 25.3176,
        "lng": 82.9739,
        "email": "nagarawas@gmail.com",
        "alt_emails": ["comm-varanasi@up.nic.in"],
        "helpline": "0542-2221711 / 1800-180-5567",
        "portal": "https://nnvns.org.in",
        "aliases": ["varanasi", "banaras", "kashi"],
    },
    {
        "name": "Agra Nagar Nigam (ANN)",
        "short": "ANN Agra",
        "city": "Agra",
        "state": "Uttar Pradesh",
        "lat": 27.1767,
        "lng": 78.0081,
        "email": "amcagra1@gmail.com",
        "alt_emails": ["nagarnigamagra@gmail.com"],
        "helpline": "0562-2520617 / 1800-180-3015",
        "portal": "https://nagarnigamagra.com",
        "aliases": ["agra", "ann"],
    },
    {
        "name": "Prayagraj Nagar Nigam",
        "short": "PNN Prayagraj",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "lat": 25.4358,
        "lng": 81.8463,
        "email": "allahabadnagarnigam@gmail.com",
        "alt_emails": ["comm.ald@gmail.com"],
        "helpline": "0532-2407963",
        "portal": "https://allahabadnagarnigam.in",
        "aliases": ["prayagraj", "allahabad"],
    },

    # Madhya Pradesh & Chhattisgarh
    {
        "name": "Indore Municipal Corporation (IMC)",
        "short": "IMC Indore",
        "city": "Indore",
        "state": "Madhya Pradesh",
        "lat": 22.7196,
        "lng": 75.8577,
        "email": "commissioner@imcindore.org",
        "alt_emails": ["imchelpline@imcindore.org"],
        "helpline": "0731-2535555 / 1800-233-1553",
        "portal": "https://imcindore.mp.gov.in",
        "aliases": ["indore", "imc"],
    },
    {
        "name": "Bhopal Municipal Corporation (BMC)",
        "short": "BMC Bhopal",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "lat": 23.2599,
        "lng": 77.4126,
        "email": "commissioner@bmconline.gov.in",
        "alt_emails": ["bhopalcorporation@gmail.com"],
        "helpline": "0755-2701000 / 155304",
        "portal": "https://www.bmconline.gov.in",
        "aliases": ["bhopal", "bmc mp"],
    },
    {
        "name": "Raipur Municipal Corporation (RMC)",
        "short": "RMC Raipur",
        "city": "Raipur",
        "state": "Chhattisgarh",
        "lat": 21.2514,
        "lng": 81.6296,
        "email": "nagarnigamraipur@gmail.com",
        "alt_emails": ["commissioner@mcraipur.in"],
        "helpline": "0771-2535780 / 1100",
        "portal": "https://mcraipur.in",
        "aliases": ["raipur", "rmc chhattisgarh"],
    },

    # Punjab, Haryana, Himachal & J&K
    {
        "name": "Municipal Corporation Chandigarh (MCC)",
        "short": "MCC Chandigarh",
        "city": "Chandigarh",
        "state": "Chandigarh",
        "lat": 30.7333,
        "lng": 76.7794,
        "email": "comm-mcc-chd@nic.in",
        "alt_emails": ["mccgrievance@gmail.com"],
        "helpline": "0172-2787200 / 155304",
        "portal": "https://mcchandigarh.gov.in",
        "aliases": ["chandigarh", "mohali", "panchkula"],
    },
    {
        "name": "Municipal Corporation Ludhiana (MCL)",
        "short": "MCL",
        "city": "Ludhiana",
        "state": "Punjab",
        "lat": 30.9010,
        "lng": 75.8573,
        "email": "commissioner.mcl@gmail.com",
        "alt_emails": ["complaintcellmcl@gmail.com"],
        "helpline": "0161-2749120",
        "portal": "https://mcludhiana.gov.in",
        "aliases": ["ludhiana", "mcl"],
    },
    {
        "name": "Municipal Corporation Amritsar (MCA)",
        "short": "MCA",
        "city": "Amritsar",
        "state": "Punjab",
        "lat": 31.6340,
        "lng": 74.8723,
        "email": "cmcamritsar@gmail.com",
        "alt_emails": ["info@amritsarcorp.com"],
        "helpline": "0183-2505500",
        "portal": "https://www.amritsarcorp.com",
        "aliases": ["amritsar"],
    },
    {
        "name": "Municipal Corporation Shimla (MCS)",
        "short": "MCS Shimla",
        "city": "Shimla",
        "state": "Himachal Pradesh",
        "lat": 31.1048,
        "lng": 77.1734,
        "email": "mcs_shimla@yahoo.com",
        "alt_emails": ["commissioner-mcs-hp@nic.in"],
        "helpline": "1916 / 0177-2802771",
        "portal": "https://shimlamc.hp.gov.in",
        "aliases": ["shimla", "mcs"],
    },
    {
        "name": "Nagar Nigam Dehradun (DNN)",
        "short": "DNN Dehradun",
        "city": "Dehradun",
        "state": "Uttarakhand",
        "lat": 30.3165,
        "lng": 78.0322,
        "email": "nagar_nigam2008@yahoo.com",
        "alt_emails": ["dehradunnagarnigam@gmail.com"],
        "helpline": "0135-2653572",
        "portal": "https://nagarnigamdehradun.com",
        "aliases": ["dehradun", "dnn"],
    },
    {
        "name": "Srinagar Municipal Corporation (SMC)",
        "short": "SMC Srinagar",
        "city": "Srinagar",
        "state": "Jammu and Kashmir",
        "lat": 34.0837,
        "lng": 74.7973,
        "email": "commissionersmc@gmail.com",
        "alt_emails": ["smc_grievance@yahoo.com"],
        "helpline": "0194-2470070 / 2474499",
        "portal": "https://www.smcsrinagar.in",
        "aliases": ["srinagar", "smc jk"],
    },

    # Kerala
    {
        "name": "Corporation of Thiruvananthapuram",
        "short": "TMC Trivandrum",
        "city": "Thiruvananthapuram",
        "state": "Kerala",
        "lat": 8.5241,
        "lng": 76.9366,
        "email": "secretary@corporationoftrivandrum.in",
        "alt_emails": ["trivandrumcorporation@gmail.com"],
        "helpline": "0471-2320821 / 0471-2377701",
        "portal": "https://tmc.lsgkerala.gov.in",
        "aliases": ["thiruvananthapuram", "trivandrum"],
    },
    {
        "name": "Kochi Municipal Corporation (KMC)",
        "short": "KMC Kochi",
        "city": "Kochi",
        "state": "Kerala",
        "lat": 9.9312,
        "lng": 76.2673,
        "email": "secretary@cochinmunicipalcorporation.mcu.in",
        "alt_emails": ["cochinmunicipality@gmail.com"],
        "helpline": "0484-2369007 / 0484-2369008",
        "portal": "https://cochinmunicipalcorporation.kerala.gov.in",
        "aliases": ["kochi", "cochin", "ernakulam"],
    },
    {
        "name": "Kozhikode Municipal Corporation",
        "short": "KMC Kozhikode",
        "city": "Kozhikode",
        "state": "Kerala",
        "lat": 11.2588,
        "lng": 75.7804,
        "email": "secretarykzd@gmail.com",
        "alt_emails": ["kozhikodecorporation@gmail.com"],
        "helpline": "0495-2323363",
        "portal": "https://kozhikodecorporation.lsgkerala.gov.in",
        "aliases": ["kozhikode", "calicut"],
    },
]


def _clean_str(val: Optional[str]) -> str:
    return (val or "").strip().lower()


def find_nearest_municipality(
    lat: float,
    lng: float,
    address_details: Optional[Dict[str, Any]] = None,
    max_radius_km: float = 80.0
) -> Dict[str, Any]:
    """
    Finds the most suitable municipal authority for a given (lat, lng) coordinate pair
    and optional OpenStreetMap address breakdown.

    Strategy:
    1. Check if the address tokens (city, town, municipality, county, state_district)
       directly match any known authority in the directory.
    2. If not an exact textual match, compute the geodesic distance to all registered
       offices. If the nearest office is within `max_radius_km`, return it.
    3. If outside known major municipal areas, generate an intelligent, inferred
       municipal authority profile using the reverse-geocoded local administrative entity.
    """
    address_details = address_details or {}

    # Gather address keywords to check for exact city matches
    extracted_tokens = set()
    for key in ("city", "town", "municipality", "city_district", "suburb", "county", "state_district", "state"):
        v = address_details.get(key)
        if v and isinstance(v, str):
            extracted_tokens.add(v.strip().lower())

    # Strategy 1: Match against known aliases if address information exists
    best_alias_match = None
    if extracted_tokens:
        for auth in MUNICIPAL_AUTHORITIES:
            aliases = {a.lower() for a in auth.get("aliases", [])}
            aliases.add(auth["city"].lower())
            if aliases.intersection(extracted_tokens):
                dist = haversine_distance(lat, lng, auth["lat"], auth["lng"])
                # Accept alias match if within reasonable distance (e.g., 120 km)
                if dist <= 120.0:
                    best_alias_match = dict(auth)
                    best_alias_match["distance_km"] = round(dist, 1)
                    best_alias_match["match_type"] = "alias_match"
                    return best_alias_match

    # Strategy 2: Geodesic proximity search across all registered municipal offices
    nearest_auth = None
    min_dist = float("inf")

    for auth in MUNICIPAL_AUTHORITIES:
        dist = haversine_distance(lat, lng, auth["lat"], auth["lng"])
        if dist < min_dist:
            min_dist = dist
            nearest_auth = auth

    if nearest_auth and min_dist <= max_radius_km:
        result = dict(nearest_auth)
        result["distance_km"] = round(min_dist, 1)
        result["match_type"] = "proximity"
        return result

    # Strategy 3: Dynamic civic entity inference based on reverse geocoded address
    city_name = (
        address_details.get("city")
        or address_details.get("town")
        or address_details.get("municipality")
        or address_details.get("county")
        or address_details.get("state_district")
        or "Local"
    ).title()

    state_name = address_details.get("state", "").title()
    clean_slug = "".join(c for c in city_name.lower() if c.isalnum()) or "civic"

    # Use closest registered authority's distance as reference if available
    dist_val = round(min_dist, 1) if nearest_auth else 0.0

    inferred_name = f"{city_name} Municipal Council / Civic Body"
    inferred_email = f"grievance.{clean_slug}@gov.in"

    # If a known regional authority is within reasonable reach, provide it as primary or alternative
    alt_emails = [f"complaints@{clean_slug}municipality.org"]
    if nearest_auth:
        alt_emails.append(f"{nearest_auth['email']} ({nearest_auth['short']} - {round(min_dist, 1)} km)")

    return {
        "name": inferred_name,
        "short": f"{city_name} ULB",
        "city": city_name,
        "state": state_name,
        "lat": lat,
        "lng": lng,
        "email": inferred_email,
        "alt_emails": alt_emails,
        "helpline": "1800-Local-Gov",
        "portal": f"https://{clean_slug}.gov.in",
        "distance_km": dist_val,
        "match_type": "inferred",
    }


def search_authorities(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Search registered municipal authorities by name, city, state, or alias.
    """
    if not query:
        return MUNICIPAL_AUTHORITIES[:limit]

    q = query.strip().lower()
    matches = []
    for auth in MUNICIPAL_AUTHORITIES:
        score = 0
        if q == auth["city"].lower() or q == auth["short"].lower():
            score = 100
        elif q in auth["name"].lower():
            score = 80
        elif q in auth["city"].lower():
            score = 70
        elif any(q in alias for alias in auth.get("aliases", [])):
            score = 60
        elif q in auth["state"].lower():
            score = 40

        if score > 0:
            matches.append((score, auth))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:limit]]
