import reapy

#load reaper project
project = reapy.Project()

#Carregas as tracks e configurá-las no reaper lendo um json e carregando os áudios

'''
Depois de preparados podemos:
1 - Começar a tocar e pausar
1.1 - dar loop e unloop do projeto
2 - mutar e desmutar tracks dependendo das selecionadas
3 - mexer nas posições das sources do encoder dos monos
4 - Ajustar a rotação binaural
5 - Fazer a comunicação com o Unity com os packets de rede
'''