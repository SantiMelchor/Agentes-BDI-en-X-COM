import matplotlib.pyplot as plt
import json
import numpy as np





with open("listas-50-150-k5-parcial.json", "r") as f:
    dicc = json.load(f)



def moving_average(x, w=10):
    return np.convolve(x, np.ones(w), 'valid') / w

res = dicc.get("soluciones")
max = 0
old = []
good = []
if res:
    for c,v in res.items():
        if v[0] > max:
            max = v[0]
            old = good
            good = []
            good.append(c)

        elif v[0] == max:
            good.append(c)
        
        elif v[0] == max -1:
            old.append(c)

    best= None
    max = 0    
    for i in good:
        suma= sum(res[i][1])
        media = suma/len(res[i][1])
        if media > max:
            max = media
            best = i
    best2= None
    max = 0    
    for i in old:
        suma= sum(res[i][1])
        media = suma/len(res[i][1])
        if media > max:
            max = media
            best2 = i

    print(best)
    print(best2)
    print(good)
    print(old)




plt.style.use("seaborn-v0_8")  
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "legend.fontsize": 10,
    "figure.figsize": (10, 5),
    "axes.spines.right": False,
    "axes.spines.top": False
})
primeros = dicc["primeros"]
ultimos = dicc["ultimos"]
media = dicc["media"]
plt.plot(primeros, label="Mejor adn", linewidth= 1.5, markersize= 6, color="#1f77b4")
#plt.plot(moving_average(primeros[:401]), label="Media adn", linewidth= 1.5, markersize= 6, color="#1f77b4")
#plt.plot(media, label="Media adn", linewidth= 1.5, markersize= 6,alpha=0.6, color="#ce4d4d")
plt.xlabel("Generacion", labelpad=8)
plt.ylabel("Fitness", labelpad=8)
plt.title("Evolucion genética BDI")
plt.legend()
plt.ylim(60,85)
#plt.xlim(0,12)
plt.grid(True)
plt.tight_layout()
plt.show()
