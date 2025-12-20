# Ce script peut générer tous les diagrammes contenus dans ce dossier. 
# 
# Instruction: 
# 1. Ajouter un dossier nommé "plantuml" à la racine du projet
# 2. Déplacer le JAR de PlantUML dans le dossier "plantuml"
# 3. Assurez-vous que votre terminal est positionné à la racine du projet
# 4. Écrivez dans le terminal: ./doc/wiki/puml/gen-uml.sh 
# 5. Tous les .puml vont générer un diagramme en SVG, pour éviter 
#    de perdre de la qualité.

for file in $(find ./doc/wiki/puml -name '*.puml')
do
    java -jar plantuml/plantuml.jar $file -svg
    #java -jar plantuml/plantuml.jar $file -png
done