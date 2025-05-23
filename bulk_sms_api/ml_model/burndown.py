import matplotlib.pyplot as plt

# Données
jours = [1, 5, 10, 15, 20]
points_restants = [100, 80, 55, 30, 0]
progression_ideale = [95, 75, 50, 25, 0]
progression_reelle = [95, 78, 52, 28, 0]

plt.figure(figsize=(10,6))
plt.plot(jours, progression_ideale, label='Progression idéale', linestyle='--', marker='o')
plt.plot(jours, progression_reelle, label='Progression réelle', linestyle='-', marker='o')
plt.plot(jours, points_restants, label='Points restants', linestyle='-.', marker='o')

plt.title('Burndown Chart du Sprint - Gestion des Campagnes')
plt.xlabel('Jour')
plt.ylabel('Points de complexité restants')
plt.xticks(jours)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
