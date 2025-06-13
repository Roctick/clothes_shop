import os
import re
import asyncio
import logging
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
from scrapers import NormScraper, NewScraper
from review_generator import generate_review
import time

logger = logging.getLogger(__name__)

# Конфигурация
ACCOUNTS = [
    {
        "name": "account_0",
        "api_id": 25568692,
        "api_hash": "709bb5b5f871c98a1d901b804f785667",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_1",
        "api_id": 25258765,
        "api_hash": "25c2436c706409dcc02cbe6c475d820d",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_2",
        "api_id": 29033861,
        "api_hash": "aa17ff0c511583dde361e5b3bd04389b",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_3",
        "api_id": 27796618,
        "api_hash": "c2f66fbe28d78b20cf1ce2dce5557fb0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_4",
        "api_id": 14772989,
        "api_hash": "40550f69480bdb036bf62c837945fecd",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_5",
        "api_id": 16740967,
        "api_hash": "658951ee881364b0d2ac2a23db2ef6f0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_6",
        "api_id": 26399415,
        "api_hash": "56465ab29cb61462cc7e7edf71572d89",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_7",
        "api_id": 23822204,
        "api_hash": "63704af7a89015d9f4cae1ae599a32ba",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_8",
        "api_id": 22765350,
        "api_hash": "d0d6b454bcf4d0ad95fdb60b5ece8a4a",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_9",
        "api_id": 21080461,
        "api_hash": "34d8edf513c1b6512a775abda1e22b4b",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_10",
        "api_id": 24287633,
        "api_hash": "3f49965dcdfb87ccc2c4b96b27dda1ee",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_11",
        "api_id": 28921238,
        "api_hash": "ee9c88b9dd7820da313fbc5bc5a818b5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_12",
        "api_id": 23476133,
        "api_hash": "a8fc97b6ebb661d22c3a34bfa772804f",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_13",
        "api_id": 27640734,
        "api_hash": "91aa2f5d71b26db0d893313af0d65bd5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_14",
        "api_id": 29989143,
        "api_hash": "427534de485ac7e7b723e5f99362bb68",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_15",
        "api_id": 27535958,
        "api_hash": "1f2bca4d7c54d76d1b2d656a2940e92b",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_16",
        "api_id": 15787212,
        "api_hash": "e868bb7caf81c444e3389998f32f4ad5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_17",
        "api_id": 19441580,
        "api_hash": "57d6d15e64611e44ec4ff199cfee7bbd",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_18",
        "api_id": 24721219,
        "api_hash": "2936539dbe6375d2f7062e58e7c164d1",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_19",
        "api_id": 11034635,
        "api_hash": "6aabebef5eb232fee7b8fd5436b46710",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_20",
        "api_id": 22260830,
        "api_hash": "f55a3b2bb046bc438863b2cc17aa25c3",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_21",
        "api_id": 21523944,
        "api_hash": "4da09e7e56a9e55c8921ef50245cae2f",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_22",
        "api_id": 20514359,
        "api_hash": "765aeff9af53e0e2028edbf139c38456",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_23",
        "api_id": 25422606,
        "api_hash": "b379fdfc9df31f7f3b6673296b077228",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_24",
        "api_id": 23685637,
        "api_hash": "1165ae497abb583076fc648ae61712b6",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_25",
        "api_id": 24361277,
        "api_hash": "7d10403e3c7c7c4a3aefb0d56c777c09",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_26",
        "api_id": 24131822,
        "api_hash": "a2ab9ca634acbba4dab978922ee0f144",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_27",
        "api_id": 22992033,
        "api_hash": "1dc73e9ed276b9bde19199d437e994ac",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_28",
        "api_id": 20056974,
        "api_hash": "f99c7bbbbefb84c01a40b6f6790d2739",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_29",
        "api_id": 24379956,
        "api_hash": "2a017092468103bea8367a35ba8f0ab6",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_30",
        "api_id": 25266025,
        "api_hash": "3a77422fcfbff2282c5c092b19867c45",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_31",
        "api_id": 26837923,
        "api_hash": "295d40757d113da7270790cda81466ba",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_32",
        "api_id": 26381108,
        "api_hash": "e2b2c59d57355f41cd214c312c856bf2",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_33",
        "api_id": 26496096,
        "api_hash": "30121a5d0996bb7677c9c1e478a93f6f",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_34",
        "api_id": 21641730,
        "api_hash": "bf1a65e6235a5ca6ce0f832987e78b87",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_35",
        "api_id": 27308117,
        "api_hash": "15df08ad35c9bd602edbed254d8bb5a1",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_36",
        "api_id": 25613756,
        "api_hash": "7820bed905628d517cdf33c1e8da8d0c",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_37",
        "api_id": 20555925,
        "api_hash": "9859ab7b7e3c9702af8e456348e43ce2",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_38",
        "api_id": 25101829,
        "api_hash": "a5ff9dd6cc7037b40f9b7e3baf160bc9",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_39",
        "api_id": 28385561,
        "api_hash": "3da11beb17c42b606a5cd8a22c7e41b7",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_40",
        "api_id": 21653513,
        "api_hash": "977615d1a208c5409a35771c7e55f672",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_41",
        "api_id": 22295117,
        "api_hash": "2433593c298bca8d7778c188e4eee741",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_42",
        "api_id": 22886417,
        "api_hash": "46cd91bf3f24d7a249bc1a9258635e89",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_43",
        "api_id": 27475628,
        "api_hash": "55c2054f453d38a39ac05ca4a358b030",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_44",
        "api_id": 27445245,
        "api_hash": "e9f7d977c409d986d2923ec0b25a3017",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_45",
        "api_id": 25825439,
        "api_hash": "32a4c704f9cb7ee8fced7ee86fe8468c",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_46",
        "api_id": 21493398,
        "api_hash": "bc28f6fbefe2297034dffbfd4cf85e57",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_47",
        "api_id": 28670146,
        "api_hash": "ece7ee5e4b711446b5710be3c8efded7",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_48",
        "api_id": 23501226,
        "api_hash": "ea4b8f2504698a4d55ddfcbc70441813",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_49",
        "api_id": 20239425,
        "api_hash": "1b2039db79e329aa851d6c3523933cc9",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_50",
        "api_id": 26816122,
        "api_hash": "33805f69162e27bea90e880083e808cf",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_51",
        "api_id": 24004085,
        "api_hash": "cef928eac1e051c900a6d0997b95298b",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_52",
        "api_id": 29762562,
        "api_hash": "b32a309780ddcb07946e02e52f04c09d",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_53",
        "api_id": 23193446,
        "api_hash": "903c23cabd9b3544d5e196a7156b3b82",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_54",
        "api_id": 24794771,
        "api_hash": "15480536afe7e06486c7b5f10cb67aa1",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_55",
        "api_id": 23479667,
        "api_hash": "d79af76424e7423812b3fd1b2a7f9225",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_56",
        "api_id": 22929173,
        "api_hash": "cc818807c3d7484d87c59846e1714cce",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_57",
        "api_id": 21108310,
        "api_hash": "bd3e15428d223c55ce5fdfb8e7141401",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_58",
        "api_id": 22473972,
        "api_hash": "508193c7975eca8a879431c416443c74",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_59",
        "api_id": 27738744,
        "api_hash": "27da6a1dc283e36c54765716f99941c9",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_60",
        "api_id": 14947427,
        "api_hash": "ae7a51f08b8bdda994cc929b93f8d95b",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_61",
        "api_id": 21428923,
        "api_hash": "a571d52705a940f114991bdabc753770",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_62",
        "api_id": 22821115,
        "api_hash": "b1bd67fc54137c9865fefda336588e9b",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_63",
        "api_id": 26959669,
        "api_hash": "239bd9d5ea12502e255ed36b61ad7820",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_64",
        "api_id": 29122279,
        "api_hash": "374d2673f9003977451e3c4b90ef7152",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_65",
        "api_id": 28290914,
        "api_hash": "03d5e40d582cf139bc2e0755aae71f52",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_66",
        "api_id": 21567409,
        "api_hash": "a8f12aeb8cb50ea1a2935d2507114462",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_67",
        "api_id": 20964566,
        "api_hash": "7212124bed7ad63ac96f5954dd5dd826",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_68",
        "api_id": 23497035,
        "api_hash": "9ef254b8979fcd3989490368da42f6ca",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_69",
        "api_id": 27406671,
        "api_hash": "b7fe56f50fe6537797ebf9bca5a4aadd",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_70",
        "api_id": 28669457,
        "api_hash": "547c543c97b16352811503b109fe5d78",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_71",
        "api_id": 27867554,
        "api_hash": "f61b2ef8f126ef946c1c2a3c88ec56b6",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_72",
        "api_id": 20669029,
        "api_hash": "46935cdce7a64765e65f65dd6ba13bb0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_73",
        "api_id": 29821088,
        "api_hash": "8de555c1582825d5db2e57958d2a03e0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_74",
        "api_id": 23782045,
        "api_hash": "e538dd430578f66587ed8c2572490de0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_75",
        "api_id": 21819139,
        "api_hash": "93dd98bea7380b45e7441ac28d72b0d2",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_76",
        "api_id": 26441583,
        "api_hash": "179318286fbd33cab921eb6ef6b49615",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_77",
        "api_id": 22237037,
        "api_hash": "b162cceac339087ea2b97a952c982bc2",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_78",
        "api_id": 24143818,
        "api_hash": "1e0cab0beff9b2619e188f27eaa0a9d9",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_79",
        "api_id": 23075739,
        "api_hash": "38abf9249afb49f90211e56f80195540",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_80",
        "api_id": 27462449,
        "api_hash": "22d025bf0976ffeb3b3284b99642d5f1",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_81",
        "api_id": 21812430,
        "api_hash": "ead5d3beb959dc3ddf48096c3095f85c",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_82",
        "api_id": 27875057,
        "api_hash": "daa70a51f4e3d7ac0b03beb7ce4628bd",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_83",
        "api_id": 25568692,
        "api_hash": "709bb5b5f871c98a1d901b804f785667",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_84",
        "api_id": 29860616,
        "api_hash": "e6fba665ce8cb36cbf938ba060b9a216",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_85",
        "api_id": 27673222,
        "api_hash": "b4efc223c57f7de0a6c9d152844898e5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_86",
        "api_id": 22128226,
        "api_hash": "d53ec3b19768c53371fcd561060bac10",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_87",
        "api_id": 23787964,
        "api_hash": "7c8c2362d05e431ab0a58b8398079a2e",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_88",
        "api_id": 27995644,
        "api_hash": "1fd45e7132df1f55b36dbe8f986c7fc2",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_89",
        "api_id": 23970320,
        "api_hash": "eefcc6f004ee8ad73dd4461fa1515b83",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_90",
        "api_id": 21146071,
        "api_hash": "18b514b654800472bd76c2f6b3fb94a3",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_91",
        "api_id": 27925169,
        "api_hash": "09b17b6d2b2882419ad0c12c8d835566",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_92",
        "api_id": 20891270,
        "api_hash": "f9d83aed3ce5296ff14286a8f5c37ad8",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_93",
        "api_id": 26310884,
        "api_hash": "a29122242edbb909667eab9ad9a91e9c",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_94",
        "api_id": 29606821,
        "api_hash": "f0ea22def473731cda8ce62dcf10560f",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_95",
        "api_id": 18124526,
        "api_hash": "6bb76bf3b8eb876c6f25fe1fa754b5e5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_96",
        "api_id": 27618719,
        "api_hash": "4f6840c1bf208028eee8a6fa66a0fe7a",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_97",
        "api_id": 25276760,
        "api_hash": "451c6a623412d354b8581d6816ea8fa1",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_98",
        "api_id": 7253181,
        "api_hash": "4bb74a8c51087214f77f69010fd8db70",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_99",
        "api_id": 20323233,
        "api_hash": "5ea3d2b815aa86d7abdb6679304f0065",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_100",
        "api_id": 27876006,
        "api_hash": "f603e77e323a29eb85e3032b6b61d7a6",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_101",
        "api_id": 27876006,
        "api_hash": "f603e77e323a29eb85e3032b6b61d7a6",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_102",
        "api_id": 26389848,
        "api_hash": "1fe90fb4f3c2628195a09ba6db79cae9",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_103",
        "api_id": 25833332,
        "api_hash": "9107d3cdd168568b4146354060599032",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_104",
        "api_id": 25568692,
        "api_hash": "709bb5b5f871c98a1d901b804f785667",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_105",
        "api_id": 23941494,
        "api_hash": "14892da8e56f1d6f9f15d07721ab4339",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_106",
        "api_id": 28786150,
        "api_hash": "7f3c5703b9fff044d58bcc55fdaf3045",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_107",
        "api_id": 21606977,
        "api_hash": "080b39dcf99e9cc3429b515109a949a0",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_108",
        "api_id": 22816030,
        "api_hash": "abb7fbd2ba4e5fabdf35318e1d8a200d",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_109",
        "api_id": 24416438,
        "api_hash": "8d86f759be2452a8b6ac1ed708440202",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_110",
        "api_id": 11224287,
        "api_hash": "51e809af3b50ecb81e3f79e091068755",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_111",
        "api_id": 18734024,
        "api_hash": "7e67011da96ecf7604c2776fb6574b93",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_112",
        "api_id": 22370723,
        "api_hash": "eeac436aeb8eccf7e5e4d9333c04c919",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_113",
        "api_id": 29870626,
        "api_hash": "79762d070b4f8db76f5a34c3e31c587c",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_114",
        "api_id": 20001831,
        "api_hash": "e589fadd890bdbb29036efe116e0a9c9",
        "target_chat": "@jobseo_bot"
    },
    {
        "name": "account_115",
        "api_id": 29761326,
        "api_hash": "4a1810a2ef01cae7f255d079922c9cf1",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_116",
        "api_id": 22033056,
        "api_hash": "9e723f4f1a4d1d7d181906a08f4455c4",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_117",
        "api_id": 28681057,
        "api_hash": "c5dd2a5acfc0e1b1e124adc309c52c08",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_118",
        "api_id": 26882643,
        "api_hash": "f2c0fcf1a09cc604c041b7f3e9401e99",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_119",
        "api_id": 21702879,
        "api_hash": "b26d9d1691b4bbeb2c4849276bb0ccf2",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_120",
        "api_id": 20066249,
        "api_hash": "13209d1908a5d9b194c7224a53eccd68",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_121",
        "api_id": 28146442,
        "api_hash": "9bb0030e546a998eaa9167ca9ed1e461",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_122",
        "api_id": 27950751,
        "api_hash": "dabcf9384a48a81622fe6bf81ac6e328",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_123",
        "api_id": 28190207,
        "api_hash": "17477f3c09b3eeaa7ddcaaa0997b2393",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_124",
        "api_id": 29661729,
        "api_hash": "41b9f524c6662b791f84fa7d87121d19",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_125",
        "api_id": 29552191,
        "api_hash": "fc7f3df055b064eb2498432b32ffc421",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_126",
        "api_id": 28750332,
        "api_hash": "333579a12efe6af2ded95b751ae7be43",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_127",
        "api_id": 28212540,
        "api_hash": "161773d3206ff26bd85c0af75a136981",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_128",
        "api_id": 24722766,
        "api_hash": "8b585adc242eb44baeae9927694255b7",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_129",
        "api_id": 21627875,
        "api_hash": "a764f88ca4338b337721f48944915caf",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_130",
        "api_id": 21833460,
        "api_hash": "4fd03209da25340d28b1617ba8d956ca",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_131",
        "api_id": 26377651,
        "api_hash": "94d51e7605b5463c75d8900077a1511c",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_132",
        "api_id": 26898217,
        "api_hash": "f9bdee409cdcacc373c24f4950590ff7",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_133",
        "api_id": 21949260,
        "api_hash": "b1f819ae1f01b321ae8a46235ad4f833",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_134",
        "api_id": 25921176,
        "api_hash": "15876e0a70bc6ed4040ac6c7d61924b0",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_135",
        "api_id": 25803849,
        "api_hash": "117a9578dc9024355cef7bcf877676b6",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_136",
        "api_id": 25568692,
        "api_hash": "709bb5b5f871c98a1d901b804f785667",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_137",
        "api_id": 26203196,
        "api_hash": "a556af9ba3b41766d3bf324d780b7423",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_138",
        "api_id": 29231751,
        "api_hash": "b61bcca5391b134ce268f7e2c337373d",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_139",
        "api_id": 20414046,
        "api_hash": "42971adc9c6c4f864972a115715d9c6f",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_140",
        "api_id": 26433869,
        "api_hash": "1ccd3bbd0f7c83476cd041c48f43a8cb",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_141",
        "api_id": 24619149,
        "api_hash": "09a108e70999e903cb0a6cbba486fa8d",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_142",
        "api_id": 25433639,
        "api_hash": "9a2f573563836185b6b735c6cdb92dd1",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_143",
        "api_id": 23976475,
        "api_hash": "f79bde92b57c5826966e2e5cf67d5875",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_144",
        "api_id": 21374551,
        "api_hash": "2c808ee58ea95e15ab2afe61f14578b5",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_145",
        "api_id": 26817339,
        "api_hash": "e6585668835c9f5418bc14faaf5bb0b3",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_146",
        "api_id": 29652818,
        "api_hash": "be6101e419653bdbbe23675b39b75a14",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_147",
        "api_id": 26831673,
        "api_hash": "2cd8100b568c80ed159a3e557446b230",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_148",
        "api_id": 21253897,
        "api_hash": "70fc6c7eb338252cedbac3ef6fddd576",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_149",
        "api_id": 22403690,
        "api_hash": "1cbf6324858c9ce9f08686fe346e79d3",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_150",
        "api_id": 20920034,
        "api_hash": "1538d240237a298b946a6b33d198a3d6",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_151",
        "api_id": 23857870,
        "api_hash": "a029343a6c9da6898c23806d86eb8fa2",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_152",
        "api_id": 25219638,
        "api_hash": "8c9f281c0d672afcbb1be62a9680101c",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_153",
        "api_id": 28828735,
        "api_hash": "3871cd4d0596551b1d7d55a602c7e1a4",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_154",
        "api_id": 20345614,
        "api_hash": "53d4c41f80f6ea49661068d09a9c10cf",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_155",
        "api_id": 26785136,
        "api_hash": "eba34ddcf41d6ecc6a0e7608e528fb24",
        "target_chat": "@jobseo_bot"
    },
        {
        "name": "account_156",
        "api_id": 22644909,
        "api_hash": "ae011b32502929230926b2fbdb95ebcb",
        "target_chat": "@jobseo_bot"
    },


]

TARGET_BOT = "@jobseo_bot"
MAX_CONCURRENT_ACCOUNTS = 60
ERROR_THRESHOLD = 3

class AccountManager:
    def __init__(self):
        self.clients = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_ACCOUNTS)
        self.account_data = {}
        self.account_clients = {}
        self.data_queue = asyncio.Queue()
        self.processed_today = 0
        self.error_threshold = ERROR_THRESHOLD  # Установка порога ошибок

    async def init_accounts(self):
        """Инициализация всех аккаунтов"""
        for acc in ACCOUNTS:
            session_path = f"sessions/{acc['name']}"
            client = TelegramClient(
                session=session_path,
                api_id=acc["api_id"],
                api_hash=acc["api_hash"]
                
            )
            self.clients.append(client)
            self.account_clients[acc["name"]] = client
            # Инициализация данных аккаунта с нужными ключами
            self.account_data[acc["name"]] = {
                "direction": None,
                "address": None,
                "blocked": False,  # Добавлено поле blocked
                "error_count": 0,   # Добавлено поле error_count
                'finished': False
            }
    async def run_selenium_in_executor(self, scraper_class, link):
        """Запускает Selenium в отдельном потоке"""
        loop = asyncio.get_running_loop()
        scraper = scraper_class(headless=True)
        return await loop.run_in_executor(None, scraper.run, link)

    def extract_link_from_message(self, message):
        """Извлекает ссылку из сообщения"""
        if not message.text:
            return None
            
        # 1. Проверяем сущности сообщения
        for entity in message.entities or []:
            if isinstance(entity, MessageEntityTextUrl):
                return entity.url
        
        # 2. Поиск URL в тексте
        url_match = re.search(r'https?://[^\s]+', message.text)
        return url_match.group(0) if url_match else None

    def extract_address_fallback(self, link: str) -> str:
        """Заглушка для обработки неизвестных ссылок"""
        logger.warning(f"Неизвестный тип ссылки: {link}")
        return "Адрес не определен"

    @staticmethod
    def extract_direction(text: str) -> str:
        """Извлекает направление из текста сообщения"""
        try:
            direction_match = re.search(r'Направление:\s*(.+)', text)
            return direction_match.group(1).strip() if direction_match else ""
        except Exception as e:
            logger.error(f"Ошибка извлечения направления: {str(e)}")
            return ""

    async def send_review(self, account_name: str, review_text: str) -> bool:
        """Отправляет отзыв через указанный аккаунт"""
        if account_name not in self.account_clients:
            logger.error(f"Аккаунт {account_name} не найден")
            return False
        
        client = self.account_clients[account_name]
        
        try:
            logger.info(f"[{account_name}] Отзыв отправлен")
            return True
        except Exception as e:
            logger.error(f"[{account_name}] Ошибка отправки: {str(e)}")
            return False

    async def start_work(self):
        """Начинает работу в 6 утра"""
        while True:
            now = datetime.datetime.now()
            if now.hour < 6:
                target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
                wait_seconds = (target_time - now).total_seconds()
                logger.info(f"Ждем до 6 утра: {wait_seconds} секунд")
                await asyncio.sleep(wait_seconds)
            
            logger.info("Начинаем работу!")
            await self.start()
            
            # Планируем следующий запуск на 6 утра следующего дня
            next_day = now + datetime.timedelta(days=1)
            next_target = next_day.replace(hour=6, minute=0, second=0, microsecond=0)
            wait_seconds = (next_target - datetime.datetime.now()).total_seconds()
            await asyncio.sleep(wait_seconds)

    async def start(self):
        """Запуск аккаунтов с ограничением"""
        tasks = []
        for client in self.clients:
            task = asyncio.create_task(self.run_account_with_throttle(client))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def run_account_with_throttle(self, client: TelegramClient):
        """Запускает аккаунт с ограничением"""
        async with self.semaphore:
            await self.handle_account(client)
            
    async def handle_account(self, client: TelegramClient):
        """Обработка аккаунта"""
        session_file = os.path.basename(client.session.filename)
        account_name = session_file.replace('.session', '')
        self.account_data[account_name]['finished'] = False  # Инициализация флага
        
        try:
            await client.start()
            logger.info(f"Аккаунт {account_name} авторизован")
            await client.send_message(TARGET_BOT, "Приступить к заданию ✍️")
            
            @client.on(events.NewMessage(from_users=TARGET_BOT))
            async def handler(event):
                await self.handle_bot_response(account_name, event.message)
                
            logger.info(f"[{account_name}] Обработчик запущен Отзыв отправлен")
            while not self.account_data[account_name].get('finished'):
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Ошибка в аккаунте {account_name}: {str(e)}", exc_info=True)
        finally:
            await client.disconnect()
            logger.info(f"[{account_name}] Аккаунт отключен")

    async def handle_bot_response(self, account_name: str, message):
        """Обработка сообщений от бота с улучшенной обработкой ошибок"""
        # Проверка блокировки аккаунта (теперь ключ гарантированно существует)
        if self.account_data[account_name]["blocked"]:
            logger.warning(f"[{account_name}] Аккаунт заблокирован, пропускаем сообщение")
            return

        try:
            text = message.text or ""
            logger.info(f"[{account_name}] Получено: {text[:50]}...")
            
            # 1. Обработка геолокации
            if any(kw in text.lower() for kw in ["геолокацию"]):
                await message.reply("Тамбов")
                logger.info(f"[{account_name}] Город отправлен")
                return
            
            elif "заблакированы" in text.lower():
                logger.info(f"[{account_name}] Аккаунт заюлокирован, выключаем аккаунт")
                self.account_data[account_name]['finished'] = True
                return
            
            elif "спасибо" in text.lower():
                logger.info(f"[{account_name}] Задание завершено, выключаем аккаунт")
                self.account_data[account_name]['finished'] = True
                return
            
            elif "Попробуйте" in text.lower():
                logger.info(f"[{account_name}] Задание сломалось, выключаем аккаунт")
                self.account_data[account_name]['finished'] = True
                return
            
            elif "недавно" in text.lower():
                logger.info(f"[{account_name}] не прошёл период, выключаем аккаунт")
                self.account_data[account_name]['finished'] = True
                return
            
            # 2. Извлечение и обработка ссылки
            if any(kw in text.lower() for kw in ["прежде чем"]):
                logger.info(f"[{account_name}] Извлекаю ссылку")
                link = self.extract_link_from_message(message)
                
                if link:
                    logger.info(f"[{account_name}] Ссылка: {link}")
                    
                    # Проверка на повторяющиеся ошибки
                    if self.account_data[account_name]["error_count"] >= self.error_threshold:
                        logger.error(f"[{account_name}] Достигнут лимит ошибок! Аккаунт заблокирован")
                        self.account_data[account_name]["blocked"] = True
                        return
                    
                    # Обработка разных типов ссылок
                    if link.startswith("https://teletype.in/"):
                        address = await self.run_selenium_in_executor(NormScraper, link)
                    elif link.startswith("https://jobseo.ru/"):
                        address = await self.run_selenium_in_executor(NewScraper, link)
                    else:
                        address = self.extract_address_fallback(link)
                    
                    # Обработка результатов скрапинга
                    if address:
                        if address.startswith(("BLOCKED_", "NETWORK_", "DRIVER_", "SCRAPER_")):
                            logger.warning(f"[{account_name}] Ошибка извлечения адреса: {address}")
                            self.account_data[account_name]["error_count"] += 1
                        else:
                            self.account_data[account_name]["address"] = address
                            self.account_data[account_name]["error_count"] = 0  # Сброс счетчика
                            logger.info(f"[{account_name}] Адрес сохранен: {address}")
                    else:
                        logger.warning(f"[{account_name}] Адрес не извлечен")
                        self.account_data[account_name]["error_count"] += 1
                    
                    # Проверка порога ошибок после увеличения счетчика
                    if self.account_data[account_name]["error_count"] >= self.error_threshold:
                        logger.error(f"[{account_name}] Достигнут лимит ошибок! Аккаунт заблокирован")
                        self.account_data[account_name]["blocked"] = True
                        return
                    
                    # Отправка команды продолжения
                    await asyncio.sleep(10)
                else:
                    logger.warning(f"[{account_name}] Ссылка не найдена")
                    self.account_data[account_name]["error_count"] += 1
                    if self.account_data[account_name]["error_count"] >= self.error_threshold:
                        logger.error(f"[{account_name}] Достигнут лимит ошибок! Аккаунт заблокирован")
                        self.account_data[account_name]["blocked"] = True
                return
            
            # 3. Продолжение задания
            elif any(kw in text.lower() for kw in ["незаконченное"]):
                time.sleep
                await message.reply("Взять новое 🔄")
                logger.info(f"[{account_name}] Продолжил")
                return
            
            # 4. Выбор платформы
            elif any(kw in text.lower() for kw in ["выберите"]):
                await message.reply("2Gis")
                logger.info(f"[{account_name}] Платформа отправлена")
                return
            
            # 5. Сохранение направления
            elif any(kw in text.lower() for kw in ["выбрали"]):
                direction = self.extract_direction(text)
                if direction:
                    self.account_data[account_name]["direction"] = direction
                    logger.info(f"[{account_name}] Направление: {direction}")
                await message.reply("Начать это задание")
                logger.info(f"[{account_name}] Задание принято")
                return
            
            # 6. Запрос логина - финальный этап
            elif any(kw in text.lower() for kw in ["логин"]):
                await asyncio.sleep(20)
                logger.info(f"[{account_name}] Запрос логина")
                
                account_data = self.account_data.get(account_name, {})
                address = account_data.get("address", "Неизвестный адрес")
                direction = account_data.get("direction", "Неизвестное направление")
                
                # Генерация и отправка отзыва
                review = generate_review(address, direction)
                success = await self.send_review(account_name, review)
                
                if success:
                    await self.data_queue.put({
                        "account": account_name,
                        "address": address,
                        "direction": direction,
                        "review": review
                    })
                    self.processed_today += 1
                    self.account_data[account_name]["error_count"] = 0  # Сброс счетчика
                    logger.info(f"[{account_name}] Данные готовы")
                return
            
            
            
            
            # 7. Обработка неизвестных сообщений
            logger.warning(f"[{account_name}] Неизвестный тип сообщения: {text[:100]}...")
            
        except Exception as e:
            logger.error(f"[{account_name}] Критическая ошибка: {str(e)}", exc_info=True)
            self.account_data[account_name]["error_count"] += 1  # Исправлено: увеличение счетчика
            
            # Блокировка аккаунта при превышении лимита ошибок
            if self.account_data[account_name]["error_count"] >= self.error_threshold:
                logger.error(f"[{account_name}] Достигнут лимит ошибок! Аккаунт заблокирован")
                self.account_data[account_name]["blocked"] = True

    async def get_parsed_data(self):
        return await self.data_queue.get()
    
    async def send_review_with_photo(self, account_name: str, review_text: str, login: str, photo_path: str) -> bool:
        """Отправляет отзыв с фото через указанный аккаунт"""
        if account_name not in self.account_clients:
            logger.error(f"Аккаунт {account_name} не найден")
            return False
        
        client = self.account_clients[account_name]
        
        try:
            
            # Шаг 2: Отправляем логин
            await client.send_message(TARGET_BOT, login)
            logger.info(f"[{account_name}] Логин отправлен: {login}")
            
            
            # Шаг 3: Отправляем фото
            await client.send_file(TARGET_BOT, photo_path)
            logger.info(f"[{account_name}] Фото отправлено")
            
            return True
        except Exception as e:
            logger.error(f"[{account_name}] Ошибка отправки: {str(e)}")
            return False