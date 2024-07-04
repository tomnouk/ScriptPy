import os
from datetime import datetime

def check_directory(path, date_limite):
	dossiers_OK = set()
	dossier_le_plus_haut = None

	for root, dirs, files in os.walk(path):
		dirs[:] = [d for d in dirs if '.git' not in d]
		tous_avant_date = True
		for file in files:
			file_path = os.path.join(root, file)
			modif_time = datetime.fromtimestamp(os.path.getmtime(file_path))
			if modif_time >= date_limite:
				tous_avant_date = False
				break
		if tous_avant_date:
			dossiers_OK.add(root)
			if dossier_le_plus_haut is None or len(root) < len(dossier_le_plus_haut):
				dossier_le_plus_haut = root
	if not dossiers_OK:
		dossier_le_plus_haut = "non non, non c'è nessun dossier"
	return {"dossier_le_plus_haut": dossier_le_plus_haut, "dossiers_OK": dossiers_OK}

if __name__ == "__main__":
	chemin_rep = "/Users/anoukmournard/Documents"
	date_limite = datetime(2023, 1, 1)
	resultat = check_directory(chemin_rep, date_limite)
	print("dossier plus haut :")
	print(resultat["dossier_le_plus_haut"])
	if resultat["dossier_le_plus_haut"] != "non non, non c'è nessun dossier":
		print("\ndossiers où tous les fichiers ont été modifiés prima della data :")
	#for dossier in resultat["dossiers_OK"]:
		#print(dossier)

