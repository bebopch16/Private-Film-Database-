# -*- coding: utf-8 -*-
# 一次性生成可手动编辑的来源文件 countries_source.txt (TSV: iso \t 中文 \t 英文)
# 之后手动编辑该 .txt，再运行 build_countries.py 重新生成 countries.js
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UN = [
    ("AF","Afghanistan","阿富汗"),("AL","Albania","阿尔巴尼亚"),("DZ","Algeria","阿尔及利亚"),
    ("AD","Andorra","安道尔"),("AO","Angola","安哥拉"),("AG","Antigua and Barbuda","安提瓜和巴布达"),
    ("AR","Argentina","阿根廷"),("AM","Armenia","亚美尼亚"),("AU","Australia","澳大利亚"),
    ("AT","Austria","奥地利"),("AZ","Azerbaijan","阿塞拜疆"),("BS","Bahamas","巴哈马"),
    ("BH","Bahrain","巴林"),("BD","Bangladesh","孟加拉国"),("BB","Barbados","巴巴多斯"),
    ("BY","Belarus","白俄罗斯"),("BE","Belgium","比利时"),("BZ","Belize","伯利兹"),
    ("BJ","Benin","贝宁"),("BT","Bhutan","不丹"),("BO","Bolivia","玻利维亚"),
    ("BA","Bosnia and Herzegovina","波斯尼亚和黑塞哥维那"),("BW","Botswana","博茨瓦纳"),
    ("BR","Brazil","巴西"),("BN","Brunei","文莱"),("BG","Bulgaria","保加利亚"),
    ("BF","Burkina Faso","布基纳法索"),("BI","Burundi","布隆迪"),("CV","Cabo Verde","佛得角"),
    ("KH","Cambodia","柬埔寨"),("CM","Cameroon","喀麦隆"),("CA","Canada","加拿大"),
    ("CF","Central African Republic","中非共和国"),("TD","Chad","乍得"),("CL","Chile","智利"),
    ("CN","China","中国"),("CO","Colombia","哥伦比亚"),("KM","Comoros","科摩罗"),
    ("CG","Congo","刚果（布）"),("CD","Democratic Republic of the Congo","刚果（金）"),
    ("CR","Costa Rica","哥斯达黎加"),("CI","Côte d'Ivoire","科特迪瓦"),("HR","Croatia","克罗地亚"),
    ("CU","Cuba","古巴"),("CY","Cyprus","塞浦路斯"),("CZ","Czechia","捷克"),
    ("DK","Denmark","丹麦"),("DJ","Djibouti","吉布提"),("DM","Dominica","多米尼克"),
    ("DO","Dominican Republic","多米尼加"),("EC","Ecuador","厄瓜多尔"),("EG","Egypt","埃及"),
    ("SV","El Salvador","萨尔瓦多"),("GQ","Equatorial Guinea","赤道几内亚"),("ER","Eritrea","厄立特里亚"),
    ("EE","Estonia","爱沙尼亚"),("SZ","Eswatini","斯威士兰"),("ET","Ethiopia","埃塞俄比亚"),
    ("FJ","Fiji","斐济"),("FI","Finland","芬兰"),("FR","France","法国"),
    ("GA","Gabon","加蓬"),("GM","Gambia","冈比亚"),("GE","Georgia","格鲁吉亚"),
    ("DE","Germany","德国"),("GH","Ghana","加纳"),("GR","Greece","希腊"),
    ("GD","Grenada","格林纳达"),("GT","Guatemala","危地马拉"),("GN","Guinea","几内亚"),
    ("GW","Guinea-Bissau","几内亚比绍"),("GY","Guyana","圭亚那"),("HT","Haiti","海地"),
    ("HN","Honduras","洪都拉斯"),("HU","Hungary","匈牙利"),("IS","Iceland","冰岛"),
    ("IN","India","印度"),("ID","Indonesia","印度尼西亚"),("IR","Iran","伊朗"),
    ("IQ","Iraq","伊拉克"),("IE","Ireland","爱尔兰"),("IL","Israel","以色列"),
    ("IT","Italy","意大利"),("JM","Jamaica","牙买加"),("JP","Japan","日本"),
    ("JO","Jordan","约旦"),("KZ","Kazakhstan","哈萨克斯坦"),("KE","Kenya","肯尼亚"),
    ("KI","Kiribati","基里巴斯"),("KP","North Korea","朝鲜"),("KR","South Korea","韩国"),
    ("KW","Kuwait","科威特"),("KG","Kyrgyzstan","吉尔吉斯斯坦"),("LA","Laos","老挝"),
    ("LV","Latvia","拉脱维亚"),("LB","Lebanon","黎巴嫩"),("LS","Lesotho","莱索托"),
    ("LR","Liberia","利比里亚"),("LY","Libya","利比亚"),("LI","Liechtenstein","列支敦士登"),
    ("LT","Lithuania","立陶宛"),("LU","Luxembourg","卢森堡"),("MG","Madagascar","马达加斯加"),
    ("MW","Malawi","马拉维"),("MY","Malaysia","马来西亚"),("MV","Maldives","马尔代夫"),
    ("ML","Mali","马里"),("MT","Malta","马耳他"),("MH","Marshall Islands","马绍尔群岛"),
    ("MR","Mauritania","毛里塔尼亚"),("MU","Mauritius","毛里求斯"),("MX","Mexico","墨西哥"),
    ("FM","Micronesia","密克罗尼西亚"),("MD","Moldova","摩尔多瓦"),("MC","Monaco","摩纳哥"),
    ("MN","Mongolia","蒙古"),("ME","Montenegro","黑山"),("MA","Morocco","摩洛哥"),
    ("MZ","Mozambique","莫桑比克"),("MM","Myanmar","缅甸"),("NA","Namibia","纳米比亚"),
    ("NR","Nauru","瑙鲁"),("NP","Nepal","尼泊尔"),("NL","Netherlands","荷兰"),
    ("NZ","New Zealand","新西兰"),("NI","Nicaragua","尼加拉瓜"),("NE","Niger","尼日尔"),
    ("NG","Nigeria","尼日利亚"),("MK","North Macedonia","北马其顿"),("NO","Norway","挪威"),
    ("OM","Oman","阿曼"),("PK","Pakistan","巴基斯坦"),("PW","Palau","帕劳"),
    ("PA","Panama","巴拿马"),("PG","Papua New Guinea","巴布亚新几内亚"),("PY","Paraguay","巴拉圭"),
    ("PE","Peru","秘鲁"),("PH","Philippines","菲律宾"),("PL","Poland","波兰"),
    ("PT","Portugal","葡萄牙"),("QA","Qatar","卡塔尔"),("RO","Romania","罗马尼亚"),
    ("RU","Russia","俄罗斯"),("RW","Rwanda","卢旺达"),("KN","Saint Kitts and Nevis","圣基茨和尼维斯"),
    ("LC","Saint Lucia","圣卢西亚"),("VC","Saint Vincent and the Grenadines","圣文森特和格林纳丁斯"),
    ("WS","Samoa","萨摩亚"),("SM","San Marino","圣马力诺"),("ST","Sao Tome and Principe","圣多美和普林西比"),
    ("SA","Saudi Arabia","沙特阿拉伯"),("SN","Senegal","塞内加尔"),("RS","Serbia","塞尔维亚"),
    ("SC","Seychelles","塞舌尔"),("SL","Sierra Leone","塞拉利昂"),("SG","Singapore","新加坡"),
    ("SK","Slovakia","斯洛伐克"),("SI","Slovenia","斯洛文尼亚"),("SB","Solomon Islands","所罗门群岛"),
    ("SO","Somalia","索马里"),("ZA","South Africa","南非"),("SS","South Sudan","南苏丹"),
    ("ES","Spain","西班牙"),("LK","Sri Lanka","斯里兰卡"),("SD","Sudan","苏丹"),
    ("SR","Suriname","苏里南"),("SE","Sweden","瑞典"),("CH","Switzerland","瑞士"),
    ("SY","Syria","叙利亚"),("TJ","Tajikistan","塔吉克斯坦"),("TH","Thailand","泰国"),
    ("TL","Timor-Leste","东帝汶"),("TG","Togo","多哥"),("TO","Tonga","汤加"),
    ("TT","Trinidad and Tobago","特立尼达和多巴哥"),("TN","Tunisia","突尼斯"),("TR","Turkey","土耳其"),
    ("TM","Turkmenistan","土库曼斯坦"),("TV","Tuvalu","图瓦卢"),("UG","Uganda","乌干达"),
    ("UA","Ukraine","乌克兰"),("AE","United Arab Emirates","阿联酋"),("GB","United Kingdom","英国"),
    ("US","United States","美国"),("UY","Uruguay","乌拉圭"),("UZ","Uzbekistan","乌兹别克斯坦"),
    ("VU","Vanuatu","瓦努阿图"),("VE","Venezuela","委内瑞拉"),("VN","Vietnam","越南"),
    ("YE","Yemen","也门"),("ZM","Zambia","赞比亚"),("ZW","Zimbabwe","津巴布韦"),
    ("TZ","Tanzania","坦桑尼亚"),
]
# 非联合国成员但片单中出现的地区（按一个中国原则，台湾不单列）
EXTRA = [
    ("HK","Hong Kong","香港"),("MO","Macao","澳门"),("PS","Palestine","巴勒斯坦"),
]
assert len(UN) == 193, f"UN={len(UN)}"

header = "# 可手动编辑：每行 = iso<TAB>中文<TAB>英文。改完运行 tools/build_countries.py 重新生成 countries.js\n"
lines = [header]
for iso, en, zh in UN + EXTRA:
    lines.append(f"{iso}\t{zh}\t{en}")
out = os.path.join(BASE, "countries_source.txt")
with open(out, "w", encoding="utf-8") as f:
    f.write("".join(l + "\n" for l in lines))
print("WROTE", out, "rows:", len(UN) + len(EXTRA))
