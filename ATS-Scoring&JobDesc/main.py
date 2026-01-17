from ats_engine import ATSSystem

resume = open("resume.txt").read()
jd = open("jd.txt").read()

ats = ATSSystem()
result = ats.analyze(resume, jd)

print(result)
