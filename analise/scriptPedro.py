###########################################################
#           VaxME - Vaccine Multi-Epitope Module          #       
#           Main Dev: Pedro Henrique Marques              #
#   For more details:                                     #
#   Please. cite us:                                      #
#                                                         #
#     Version 1.0                                         #                                      
###########################################################
#Librarys and modules
import os, pandas as pd, selenium, shutil, random, zipfile, time, subprocess, threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.shortcuts import redirect



proteinas_lista = []

# Lista dos arquivos a serem verificados e removidos
arquivos_para_apagar = [
    "Chimeric.faa",
    "Chimeric.input.tsv",
    "Chimeric.result.tsv",
    "Chimeric_result.csv",
    "FinalEpitopes.txt",
    "MHCII_Epitopes_1.txt",
    "MHCII_Epitopes_2.txt",
    "MHCII_Epitopes_3.txt",
    "MHCI_Epitopes_1.txt",
    "MHCI_Epitopes_2.txt",
    "MHCI_Epitopes_3.txt",
    "ResultCluster1.csv",
    "ResultCluster1.txt",
    "ResultCluster2.csv",
    "ResultCluster2.txt",
    "VaxignML.sh",
    "Your_Final_Epitopes.txt",
    "analise/__pycache__/limpar.cpython-312.pyc",
    "cluster1.txt",
    "cluster2.txt",
    "email.str",
    "greaterthan11.txt",
    "laststep.txt",
    "lessthan11.txt",
    "output.csv",
    "Allertop.png",
    "Final.zip",
    "FinalSemCabeca.txt",
    "MHCintermediariesFILES.zip",
    "ProtParam.txt",
    "ProtParam.txt",
    "PsiPred.txt",
    "YourFinalModel.faa",
    "flowchart.png",
    "sequence.png"
]

# Remover os arquivos se existirem
for arquivo in arquivos_para_apagar:
    if os.path.exists(arquivo):
        os.remove(arquivo)
        print(f"Arquivo removido: {arquivo}") 

#1.0 - First module - comunication with the HTML
def dataform(data_dict):
    projeto = data_dict['analysisnameform']
    useremail = data_dict['emailform']
    proteinas = data_dict['proteinsseqfileform']
    allelesmchi = data_dict['mhcIform']
    allelesmchii = data_dict['mhcIIform']
    metodoMHCI = data_dict['methodsMHCIform']
    metodoMHCII = data_dict['methodsMHCIIform']
    tmMHCI = data_dict['tmMHCI']
    tmMHCII = data_dict['tmMHCII']
    p1 = data_dict['p1form']
    p2 = data_dict['p2form']
    ic50mhc1 = data_dict['IC50MHCIform']
    ic50mhc2 = data_dict['IC50MHCIIform']
    number_chimerics = data_dict['chimericmodelsnumberform']
    linkermhc1 = data_dict['mhcILinkerform']
    linkermhc2 = data_dict['mhcIILinkerform']
    adjuvante = data_dict['adjuvantform']

    #1.1.1 Processing Sequence
    proteinsequencelist = []
    for protein in proteinas:
        p = protein
        proteinsequencelist.append(p[1])

    #1.2.1 Processing MHC1 alleles
    allelesmchicomma = []
    for allei in allelesmchi:
        a = f'{allei},'
        allelesmchicomma.append(a)
    allelesmchilast = allelesmchicomma[-1].replace(',', '')
    allelesmhciadjust = allelesmchicomma[:-1]
    allelesmhciadjust.append(allelesmchilast)
    allelesmhcifinal = ''.join(allelesmhciadjust)

    #1.2.2 Processing MHC2 alleles
    allelesmchiicomma = []
    for allei in allelesmchii:
        a = f'{allei},'
        allelesmchiicomma.append(a)
    allelesmchiilast = allelesmchiicomma[-1].replace(',', '')
    allelesmhciiadjust = allelesmchiicomma[:-1]
    allelesmhciiadjust.append(allelesmchiilast)
    allelesmhciifinal = ''.join(allelesmhciiadjust)

    #1.3.1 Processing MHC1 alleles size
    tmmhcicomma = []
    for tm in allelesmchi:
        tam = f'{tmMHCI},'
        tmmhcicomma.append(tam)
    tmhcilast = tmmhcicomma[-1].replace(',', '')
    tmhciadjust =  tmmhcicomma[:-1]
    tmhciadjust.append(tmhcilast)
    tmhcifinal = ''.join(tmhciadjust)

    #1.3.2 Processing MHC alleles size
    tmmhciicomma = []
    for tm in allelesmchii:
        tam = f'{tmMHCII},'
        tmmhciicomma.append(tam)
    tmhciilast = tmmhciicomma[-1].replace(',', '')
    tmhciiadjust = tmmhciicomma[:-1]
    tmhciiadjust.append(tmhciilast)
    tmhciifinal = ''.join(tmhciiadjust)

    return (projeto, useremail, proteinsequencelist, allelesmhcifinal, allelesmhciifinal, metodoMHCI, metodoMHCII, tmhcifinal, tmhciifinal, p1, p2, ic50mhc1, ic50mhc2, number_chimerics,linkermhc1,linkermhc2,adjuvante)

#2.0 - Second module - Epitope Prediction from IEDB and ABCpred
#2.1 Django data extraction for the back-end script
def predicao(data):
    projeto = data[0]
    useremail = data[1]
    proteinsequencelist = data[2]
    allelesmhcifinal = data[3]
    allelesmhciifinal =data[4]
    metodoMHCI = data[5]
    metodoMHCII = data[6]
    tmhcifinal = data[7]
    tmhciifinal = data[8]
    p1 = data[9]
    p2 = data[10]
    ic50mhc1 = data[11]
    ic50mhc2 = data[12]
    number_chimerics = data[13]
    linkermhci = data[14]
    linkermhcii = data[15]
    adjuvantevacina = data[16]
    

    headers = [
    'Targets', 'MHCI pred', 'MHCI pred2', 'MHCII pred', 'MHCII pred2',
    'Bcell', 'MHCI fil1', 'MHCI fil2', 'MHCII fil1', 'MHCII fil2',
    'MHCI over1', 'MHCII over1', 'MHCI over2', 'MHCII over2', 'MHCI final', 'MHCII final'
    ]

    # Criar o arquivo de texto e escrever os headers na primeira linha
    with open('output.csv', 'w') as arquivo:
        arquivo.write(','.join(headers) + '\n')


#2.2 IEDB epitope prediction via CURL-
    key = 0
    for targets in proteinsequencelist:
        key = key + 1
        convertion = str(key)
        with open("chaveamento" + convertion + ".txt","w") as keys:
            keys.write(convertion + "" + targets)
        key_folders = "./keys/"
        os.replace("./chaveamento"+convertion+".txt", key_folders + "chaveamento"+convertion+".txt")
        comando1 = 'curl --data "method=' + "recommended" + '&sequence_text=' + f"{targets}" + '&allele=' + f"{allelesmhcifinal}" + '&length=' + f"{tmhcifinal}" + '" http://tools-cluster-interface.iedb.org/tools_api/mhci/ > IEDBmhci.txt'
        comando2 = 'curl --data "method=' + f"{metodoMHCI}" + '&sequence_text=' + f"{targets}" + '&allele=' + f"{allelesmhcifinal}" + '&length=' + f"{tmhcifinal}" + '" http://tools-cluster-interface.iedb.org/tools_api/mhci/ > NETmhci.txt'
        comando3 = 'curl --data "method=' + "recommended" + '&sequence_text=' + f"{targets}" + '&allele=' + f"{allelesmhciifinal}" + '&length=' + f"{tmhciifinal}" + '" http://tools-cluster-interface.iedb.org/tools_api/mhcii/ > IEDBmhcii.txt'
        comando4 = 'curl --data "method=' + f"{metodoMHCII}" + '&sequence_text=' + f"{targets}" + '&allele=' + f"{allelesmhciifinal}" +'&length=' + f"{tmhciifinal}" + '" http://tools-cluster-interface.iedb.org/tools_api/mhcii/ > NETmhcii.txt'
        os.system(comando1)
        os.system(comando2)
        os.system(comando3)
        os.system(comando4)

        #2.2.1 Convert the output file of the curl method (.txt) into a csv file to work in pandas
        #2.2.1.1 MHC1 IEDB and another option
        abrir = pd.read_csv("IEDBmhci.txt", sep="	")
        abrir.to_csv('IEDBmhci.csv',  
                        index = None)
        os.remove("IEDBmhci.txt")
        ###  ###  ###
        abrirNETmhci = pd.read_csv("NETmhci.txt", sep="	")
        abrirNETmhci.to_csv('NETmhci.csv',  
                         index = None)
        os.remove("NETmhci.txt")

        #2.2.1.2 MHC2 IEDB and another option
        abrirIEDBmhcii = pd.read_csv("IEDBmhcii.txt", sep="	")
        abrirIEDBmhcii.to_csv('IEDBmhcii.csv',  
                          index = None)
        os.remove("IEDBmhcii.txt")
        ###  ###  ###
        abrirNETmhcii = pd.read_csv("NETmhcii.txt", sep="	")
        abrirNETmhcii.to_csv('NETmhcii.csv',  
                          index = None)
        os.remove("NETmhcii.txt")

#2.3 ABCpred prediction via selenium
        #2.3.1 Firefox headless option
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        nav = webdriver.Firefox(options=firefox_options)
        time.sleep(2)
        nav.get("https://webs.iiitd.edu.in/raghava/abcpred/ABC_submission.html")
        time.sleep(5)
        #2.3.2 Getting elements
        nav.find_element(By.XPATH, '/html/body/form/font/textarea').send_keys(targets)
        nav.find_element(By.XPATH,'/html/body/form/p[2]/input[2]').click()
        time.sleep(15)
        #2.3.3 Storing results
        tabeladonav = nav.find_element(By.XPATH, '/html/body/pre[2]/table/tbody')
        lernav = tabeladonav.text
        nav.close()
        #2.3.4 Converting the ABCpred output to csv file
        with open("Bcell0.csv", "w") as f:
            f.writelines(lernav)
        lerBcell = pd.read_csv("Bcell0.csv", sep=" ")
        lerBcell.to_csv('Bcell.csv',  
                          index = None)
        os.remove("Bcell0.csv")

        #3.0 Filtering the epitopes by IC50 and percentil rank
        #3.1.1 Filtering MHC1 epitopes by IEDB recommeded method
        df = pd.read_table("IEDBmhci.csv", sep = ',')
        cortado = df.filter(["allele","peptide","percentile_rank"])
        filtrado = cortado[(cortado["percentile_rank"] <=p1)]
        filtrado.to_csv('IEDBmhc1FIL.csv',  
                                  index = None)
        #3.1.2 Filtering MHC1 epitopes by another method
        if "consensus" in metodoMHCI:
            Metodo2MHCI = pd.read_table("NETmhci.csv", sep = ',')
            Metodo2MHCIcolunas = Metodo2MHCI.filter(["allele","peptide","ann_ic50","consensus_percentile_rank"])
            Metodo2MHCIfiltro = Metodo2MHCIcolunas[(Metodo2MHCIcolunas["ann_ic50"] <ic50mhc1) & (Metodo2MHCIcolunas["consensus_percentile_rank"] < p1)]
            duplicateMHCI = Metodo2MHCIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCI.to_csv('NETmhc1FIL.csv',  
                            index = None)

        elif "netmhcpan_ba" in metodoMHCI or "ann" in metodoMHCI or "smmpmbec" in metodoMHCI or "smm" in metodoMHCI or "netmhccons" in metodoMHCI or "pickpocket" in metodoMHCI:
            Metodo2MHCI = pd.read_table("NETmhci.csv", sep = ',')
            Metodo2MHCIcolunas = Metodo2MHCI.filter(["allele","peptide","ic50","percentile_rank"])
            Metodo2MHCIfiltro = Metodo2MHCIcolunas[(Metodo2MHCIcolunas["ic50"] <ic50mhc1) & (Metodo2MHCIcolunas["percentile_rank"] < p1)]
            duplicateMHCI = Metodo2MHCIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCI.to_csv('NETmhc1FIL.csv',  
                            index = None)

        elif "netmhcpan_el" in metodoMHCI:
            Metodo2MHCI = pd.read_table("NETmhci.csv", sep = ',')
            Metodo2MHCIcolunas = Metodo2MHCI.filter(["allele","peptide","percentile_rank"])
            Metodo2MHCIfiltro = Metodo2MHCIcolunas[(Metodo2MHCIcolunas["percentile_rank"] < p1)]
            duplicateMHCI = Metodo2MHCIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCI.to_csv('NETmhc1FIL.csv',  
                            index = None)

        elif "netmhcstabpan" in metodoMHCI:
            Metodo2MHCI = pd.read_table("NETmhci.csv", sep = ',')
            Metodo2MHCIcolunas = Metodo2MHCI.filter(["allele","peptide","percentile_rank"])
            Metodo2MHCIfiltro = Metodo2MHCIcolunas[(Metodo2MHCIcolunas["percentile_rank"] < p1)]
            duplicateMHCI = Metodo2MHCIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCI.to_csv('NETmhc1FIL.csv',  
                            index = None)
        
        #3.2.1 Filtering MHC2 epitopes by IEDB recommeded method
        df1 = pd.read_table("IEDBmhcii.csv", sep = ',')
        tirar = df1.replace('-', 0)
        tirar.to_csv('tirado.csv',  
                      index = None)
        jatirado = pd.read_table("tirado.csv", sep = ',')
        cortado1 = jatirado.filter(["allele","peptide", "rank"])
        filtrado1 = cortado1[(cortado1["rank"]<p2)]
        filtrado1.to_csv('IEDBmhc2FIL.csv',  
                  index = None)
        os.remove('tirado.csv')

        #3.2.2 Filtering MHC2 epitopes by another method
        
        if "NetMHCIIpan" in metodoMHCII or "nn_align" in metodoMHCII or "smm_align" in metodoMHCII:
            Metodo2MHCII = pd.read_table("NETmhcii.csv", sep = ',')
            Metodo2MHCIIcolunas = Metodo2MHCII.filter(["allele","peptide","ic50","rank"])
            Metodo2MHCIIfiltro = Metodo2MHCIIcolunas[(Metodo2MHCIIcolunas["ic50"] <ic50mhc2) & (Metodo2MHCIIcolunas["rank"] < p2)]
            duplicateMHCII = Metodo2MHCIIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCII.to_csv('NETmhc2FIL.csv',  
                            index = None)
        elif "comblib" in metodoMHCII:
            Metodo2MHCII = pd.read_table("NETmhcii.csv", sep = ',')
            Metodo2MHCIIcolunas = Metodo2MHCII.filter(["allele","peptide","rank"])
            Metodo2MHCIIfiltro = Metodo2MHCIIcolunas[(Metodo2MHCIIcolunas["rank"] < p2)]
            duplicateMHCII = Metodo2MHCIIfiltro.drop_duplicates(subset='peptide', keep="first")
            duplicateMHCII.to_csv('NETmhc2FIL.csv',  
                            index = None)



        #OBS: CHECKPOINT to save the first prediction data and quantify epitopes by tool

        dados = pd.read_csv("IEDBmhci.csv")
        numero_linhas = len(dados)
        IEDBmhci_valor_pred = numero_linhas - 1
        qntdIEDB1 = str(IEDBmhci_valor_pred)

        dados2 = pd.read_csv("IEDBmhcii.csv")
        numero_linhas2 = len(dados2)
        IEDBmhcii_valor_pred = numero_linhas2 - 1
        qntdIEDB2 = str(IEDBmhcii_valor_pred)

        dados3 = pd.read_csv("NETmhci.csv")
        numero_linhas3 = len(dados3)
        NETmhci_valor_pred = numero_linhas3 - 1
        qntdNET1 = str(NETmhci_valor_pred)

        dados4 = pd.read_csv("NETmhci.csv")
        numero_linhas4 = len(dados4)
        NETmhcii_valor_pred = numero_linhas4 - 1
        qntdNET2 = str(NETmhcii_valor_pred)

        dados5 = pd.read_csv("Bcell.csv")
        numero_linhas5 = len(dados5)
        ABC_valor = numero_linhas5 - 1
        qntdABC = str(ABC_valor)
        #PREDICTED
        print("\n\nAs quantidades de epítopos preditos foram "+qntdIEDB1 + ", "+ qntdIEDB2 + ", "+ qntdNET1 + ", "+ qntdNET2 + ", "+ qntdABC)  

        #OBS: CHECKPOINT to save the data filtered

        dadosfil = pd.read_csv("IEDBmhc1FIL.csv")
        numero_linhasfil = len(dadosfil)
        IEDBmhci_valor_predfil = numero_linhasfil
        qntdIEDB1fil = str(IEDBmhci_valor_predfil)

        dadosfil2 = pd.read_csv("IEDBmhc2FIL.csv")
        numero_linhas2fil = len(dadosfil2)
        IEDBmhcii_valor_predfil = numero_linhas2fil
        qntdIEDB2fil = str(IEDBmhcii_valor_predfil)

        dadosfil3 = pd.read_csv("NETmhc1FIL.csv")
        numero_linhas3fil = len(dadosfil3)
        NETmhci_valor_predfil = numero_linhas3fil
        qntdNET1fil = str(NETmhci_valor_predfil)

        dadosfil4 = pd.read_csv("NETmhc2FIL.csv")
        numero_linhas4fil = len(dadosfil4)
        NETmhcii_valor_predfil = numero_linhas4fil
        qntdNET2fil = str(NETmhcii_valor_predfil)
        #FILTERED
        print("\n\nAs quantidades de epítopos restantes após filtrar foram "+qntdIEDB1fil + ", "+ qntdIEDB2fil + ", "+ qntdNET1fil + ", "+ qntdNET2fil)  
        


        os.remove("IEDBmhci.csv")
        os.remove("IEDBmhcii.csv")
        os.remove("NETmhci.csv")
        os.remove("NETmhcii.csv")

        #4.0 Overlapping between MHC1 x MHC1 tools, MHC2 x MHC2 tools and Bcell x MHC1 final and Bcell x MHC2 final
        #4.1 MHC1 overlapping
        #4.1.1 Processing MHC 1 filtered files
        oldIEDB1 = pd.read_table("IEDBmhc1FIL.csv", sep=',')
        newIEDB1 = oldIEDB1[['peptide']]
        renome = newIEDB1.rename(columns={'peptide': 'epitopo'})
        renome.to_csv('IEDBepi1.csv',  
                          index = None)

        ### ### ###
        oldNET1 = pd.read_table("NETmhc1FIL.csv", sep=',')
        newNET1 = oldNET1[['peptide']]
        renome1 = newNET1.rename(columns={'peptide': 'epitopo'})
        renome1.to_csv('NETepi1.csv',  
                        index = None)
        #4.1.2 Overlapping MHCI IEDB recommeded method x another MHC1 prediction method
        exec(open("epitopo1.py").read())

        #4.2 MHC2 overlapping
        #4.2.1 Processing MHC2 filtered files
        oldIEDB2 = pd.read_table("IEDBmhc2FIL.csv", sep=',')
        newIEDB2 = oldIEDB2[['peptide']]
        renome3 = newIEDB2.rename(columns={'peptide': 'epitopo'})
        renome3.to_csv('IEDBepi2.csv',  
                          index = None)
        ### ### ###
        oldNET2 = pd.read_table("NETmhc2FIL.csv", sep=',')
        newNET2 = oldNET2[['peptide']]
        renome4 = newNET2.rename(columns={'peptide': 'epitopo'})
        renome4.to_csv('NETepi2.csv',  
                          index = None)
        #4.2.2 Overlapping MHCI IEDB recommeded method x another MHC1 prediction method
        exec(open("epitopo2.py").read())

        #4.3 Bcell overlapping
        #4.3.1 Processing MHC1 overlapped and filtered files
        src=r'IEDBepi1.csv_NETepi1.csv_9_out.txt'
        des=r'IEDBepi1xNETepi19.csv'
        shutil.copy(src, des)
        Bcell1 = pd.read_table("IEDBepi1xNETepi19.csv", sep = ',')
        Preparado1 = Bcell1[["epitope_1"]]
        dups1 = Preparado1.drop_duplicates(subset='epitope_1', keep="first")
        renomear = dups1.rename(columns={'epitope_1': 'epitopo'})
        renomear.to_csv('MHC1overlap.csv',  
                          index = None)
        
        #4.3.2 Processing MHC2 overlapped and filtered files
        src1=r'IEDBepi2.csv_NETepi2.csv_15_out.txt'
        des1=r'IEDBepi2xNETepi215.csv'
        shutil.copy(src1, des1)
        Bcell2 = pd.read_table("IEDBepi2xNETepi215.csv", sep = ',')
        Preparado2 = Bcell2[["epitope_1"]]
        dups2 = Preparado2.drop_duplicates(subset='epitope_1', keep="first")
        renomear1 = dups2.rename(columns={'epitope_1': 'epitopo'})
        renomear1.to_csv('MHC2overlap.csv',  
                          index = None)
        #OVERLLAPED
        dadosfilover = pd.read_csv("MHC1overlap.csv")
        numero_linhasfilover = len(dadosfilover)
        MHC1filover= numero_linhasfilover
        MHC1filover1 = str(MHC1filover)

        dadosfilover2 = pd.read_csv("MHC2overlap.csv")
        numero_linhasfilover2 = len(dadosfilover2)
        MHC2filover= numero_linhasfilover2
        MHC2filover2 = str(MHC2filover)

        print("número de epítopos overlapped entre ferramentas de MHCI é "+ MHC1filover1 + ", e número de MHCII é " + MHC2filover2)

        #4.3.3 Processing Bcell filtered files
        BcellREAL = pd.read_table("Bcell.csv", sep = ',')
        Colunar = BcellREAL[["Sequence"]]
        renomear2 = Colunar.rename(columns={'Sequence': 'epitopo'})
        temnadak = renomear2.dropna()
        temnadak.to_csv('BcellPrepared.csv',  
                        index = None)
        #4.4 Overlapping Bcell x MHC1 and MHC2 filtered and overlapped
        exec(open("Bcell9.py").read())
        exec(open("Bcell15.py").read())

        #5.0 Selection of the final MHCI and MHCII epitopes to design the multi-epitope vaccine sequence
        LeituraFinal = pd.read_csv("MHC1overlap.csv_BcellPrepared.csv_9_out.txt", sep = ",")
        SelecionandoOsTop = LeituraFinal[["kmer"]]
        DuplicadosTop = SelecionandoOsTop.drop_duplicates(subset='kmer', keep="first")
        DuplicadosTop.to_csv('MHCI_Epitopes_'+convertion+".txt",  
                        index = None)
        MHC1xBcell = len(DuplicadosTop)
        MHC1xBcellnumber = str(MHC1xBcell)
    
        LeituraFinalMHCII = pd.read_csv("MHC2overlap.csv_BcellPrepared.csv_15_out.txt", sep = ",")
        SelecionandoOsTop2 = LeituraFinalMHCII[["kmer"]]
        DuplicadosTop2 = SelecionandoOsTop2.drop_duplicates(subset='kmer', keep="first")
        DuplicadosTop2.to_csv('MHCII_Epitopes_' + convertion + ".txt",  
                        index = None)
        MHC2xBcell = len(DuplicadosTop2)
        MHC2xBcellnumber = str(MHC2xBcell)

        print("epítopos finais, overlapped com Bcell para MHCI, " + MHC1xBcellnumber + ", para MHCII é " + MHC2xBcellnumber)
        
        search_text11 = "kmer\n"
        replace_text11 = ""
        #5.1 Creating the final files: create a file of MHC1 final epitopes and another file for MHC2 final epitopes for each protein.
        with open("MHCI_Epitopes_"+convertion+".txt",'r') as file11:
            data11 = file11.read()
            data11 = data11.replace(search_text11, replace_text11)
        with open('MHCI_Epitopes_'+convertion+".txt", 'w') as file12:
            file12.write(data11)
        
        with open("MHCII_Epitopes_"+convertion+".txt", 'r') as file22:
            data22 = file22.read()
            data22 = data22.replace(search_text11, replace_text11)
        with open('MHCII_Epitopes_'+convertion+".txt", 'w') as file22:
            file22.write(data22)

        proteinas_lista.append(convertion)
        stringado_convertion = str(convertion)
        
        #Generating csv to be the Output

            # output
        with open('output.csv', 'a') as output:
            linhadoout = ','.join([
                stringado_convertion, qntdIEDB1, qntdNET1, qntdIEDB2, qntdNET2,
                qntdABC, qntdIEDB1fil, qntdNET1fil, qntdIEDB2fil, qntdNET2fil,
                MHC1filover1, MHC2filover2, MHC1xBcellnumber, MHC2xBcellnumber])
            output.write(linhadoout + '\n')

        #5.2 Clear the folder
        #OBS2: CHECKPOINT to save the filtered and overlapped epitopes
        os.remove("Bcell.csv")
        os.remove("BcellPrepared.csv")
        os.remove("IEDBepi1.csv")
        os.remove("IEDBepi1xNETepi19.csv")
        os.remove("IEDBepi2.csv")
        os.remove("IEDBepi2xNETepi215.csv")
        os.remove("IEDBmhc1FIL.csv")
        os.remove("IEDBmhc2FIL.csv")
        os.remove("MHC1overlap.csv")
        os.remove("MHC2overlap.csv")
        os.remove("NETepi1.csv")
        os.remove("NETepi2.csv")
        os.remove("NETmhc1FIL.csv")
        os.remove("NETmhc2FIL.csv")
        #Remove all the txt files from the overlapping
        pasta = './'
        for diretorio, subpastas, arquivos in os.walk(pasta):
            for arquivo in arquivos:
                if "out.txt" in arquivo:
                    os.remove(arquivo)  
    proteinas_lista_tratada = list(set(proteinas_lista))
    proteinas_lista_tratada = [f"Protein{proteina}" for proteina in proteinas_lista_tratada]
    print(proteinas_lista_tratada)

    #6.0 Processing the Final Epitopes by the MHC1 immunogenicity
    #6.1 Processing file 
    os.system("cat *.txt > FinalEpitopes.txt")
    search_For = ""
    replace_for = ""
    with open("FinalEpitopes.txt",'r') as fileFINAL:
        dataFINAL = fileFINAL.read()
        dataFINAL = dataFINAL.replace(search_For, replace_for)
    with open("FinalEpitopes.txt", 'w') as fileFINAL2:
        fileFINAL2.write(dataFINAL)
    
    #6.2 Separation of epitopes smaller than 11 (which will go to MHCI immunogenicity) and larger than 11.
    minorepitopes = open("FinalEpitopes.txt", "r") 
    listminorepitopes = [line.rstrip('\n') for line in open("FinalEpitopes.txt")]
    listlongerthan11 = []
    listshorterthan11 = []
    for epitope in listminorepitopes:
            if len(epitope) <11:
                listshorterthan11.append(epitope)
            else:
                listlongerthan11.append(epitope)
    with open("greaterthan11.txt","w") as maiorque11:
        for epitope in listlongerthan11:
            maiorque11.writelines(epitope+"\n")
    with open("lessthan11.txt","w") as menorque11:
        for epitope in listshorterthan11:
            menorque11.writelines(epitope+"\n")

    #6.3 MHCI immunogenicity using for MHCI epitopes (i.e less than 11 aa)
    MHCinav = webdriver.Firefox(options=firefox_options)
    MHCinav.get("http://tools.iedb.org/immunogenicity/")    
    MHCinav.find_element(By.XPATH, '//*[@id="id_sequence_file"]').send_keys(os.getcwd()+'/lessthan11.txt')
    time.sleep(5)
    MHCinav.find_element(By.XPATH, '//*[@id="input-form"]/table/tbody/tr[6]/th/div/input[1]').click()
    time.sleep(10)
    tabeladoMHCIClass = MHCinav.find_element(By.XPATH, '//*[@id="result_table"]')
    tabeladonavegadorMHCIclass = tabeladoMHCIClass.text
    MHCinav.close()
    quebradelinha = "Peptide\n"
    virgula = "Peptide,"
    quebradordelinhas= "Peptide,Length\n"
    quebradordelinhas1= "Peptide,Length,"
    trocatrocadetxt = " "
    trocatrocadnv = ","
    with open("lessthan11.txt","w") as finaldosepitops:
        finalizarosepitopos = finaldosepitops.writelines(tabeladonavegadorMHCIclass)
    with open("lessthan11.txt","r") as reading:
        finalizadinho = reading.read()
        finalizadinho = finalizadinho.replace(quebradelinha,virgula)
    with open("lessthan11.txt", "w") as filepequeno:
        filepequeno.write(finalizadinho)
    with open("lessthan11.txt","r") as reading1:
        finalizadinho1 = reading1.read()
        finalizadinho1 = finalizadinho1.replace(quebradordelinhas,quebradordelinhas1)
    with open("lessthan11.txt", "w") as filepequeno1:
        filepequeno1.write(finalizadinho1)
    with open("lessthan11.txt","r") as reading12:
        finalizadinho12 = reading12.read()
        finalizadinho12 = finalizadinho12.replace(trocatrocadetxt,trocatrocadnv)
    with open("lessthan11.txt", "w") as filepequeno12:
        filepequeno12.write(finalizadinho12)
    Finish = pd.read_csv("lessthan11.txt",sep=",")
    filtered_epitopes = Finish[(Finish["Score"]>0.1)]
    MHCI_immunogenicity_analysis = filtered_epitopes[["Peptide"]]
    MHCI_immunogenicity_analysis.to_csv("lessthan11.txt", header=None, index=None)
    MHCIimmuno = len(MHCI_immunogenicity_analysis)
    MHCIimmunoNumber = str(MHCIimmuno)
    print("Os epítopos de MHCI foram reduzidos para " + MHCIimmunoNumber + " após MHCI immunogenicity")

    #6.4 List of the final epitopes (MHC1 with immunogenicity avaliation) + (MHCII)
    with open("lessthan11.txt", 'r') as file1, open("greaterthan11.txt", 'r') as file2, open("FinalEpitopes.txt", 'w') as output_file:
        for linha in file1:
            output_file.write(linha)
        for linha in file2:
            output_file.write(linha)

    #OBS: Importing the parameters for vaccine development
    Multi_Chimeric = number_chimerics
    Linker1 = linkermhci
    Linker2 = linkermhcii
    Adjuvant = adjuvantevacina
    epitopes = open("FinalEpitopes.txt", "r")
    linebyline = epitopes.readlines()

    resultados = []

    for x in linebyline:
        resultados.append(x.replace("\n", ""))
        transformar = "".join(resultados)
        arquivo = open("FinalEpitopes.txt", "r")
        lista = [line.rstrip('\n') for line in open("FinalEpitopes.txt")]

    #7.0 Epitope cluster analysis
    #7.1 Separation again
    arquivofinalepitopes = open("FinalEpitopes.txt", "r")
    listafinalepitopes = [line.rstrip('\n') for line in open("FinalEpitopes.txt")]
    listamaiorque11 = []
    listamenorque11 = []
    for epitope in listafinalepitopes:
            if len(epitope) <11:
                listamenorque11.append(epitope)
            else:
                listamaiorque11.append(epitope)
    with open("greaterthan11.txt","w") as maiorque11:
        for epitope in listamaiorque11:
            maiorque11.writelines(epitope+"\n")
    with open("lessthan11.txt","w") as menorque11:
        for epitope in listamenorque11:
            menorque11.writelines(epitope+"\n")

    #7.2 Epitope Cluster Analysis
    #7.2.1 ECA MHC1
    clusters = webdriver.Firefox(options=firefox_options)
    clusters.get("http://tools.iedb.org/cluster/")    
    clusters.find_element(By.XPATH, '//*[@id="id_sequence_file"]').send_keys(os.getcwd()+"/lessthan11.txt") #Pra epitopos menor que 11
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[5]/th/div/input[1]').click()
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[7]/th/div/input[2]').click()
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[4]/th/div/input[2]').click()
    time.sleep(2)
    tabeladoclusters = clusters.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[2]/div[1]/table/tbody')
    tabeladonavegadorclusters = tabeladoclusters.text
    Clustermenorque11 = tabeladonavegadorclusters
    clusters.close()
    #7.2.2 ECA MHC2
    clusters = webdriver.Firefox(options=firefox_options)
    clusters.get("http://tools.iedb.org/cluster/")    
    clusters.find_element(By.XPATH, '//*[@id="id_sequence_file"]').send_keys(os.getcwd()+"/greaterthan11.txt") #Pra epitopos maior que 11
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[5]/th/div/input[1]').click()
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[7]/th/div/input[2]').click()
    time.sleep(1)
    clusters.find_element(By.XPATH, '/html/body/div[3]/form/table/tbody/tr[4]/th/div/input[2]').click()
    time.sleep(2)
    tabeladoclusters = clusters.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[2]/div[1]/table/tbody')
    tabeladonavegadorclustersmaiorque11 = tabeladoclusters.text
    Clustermaiorque11 = tabeladonavegadorclustersmaiorque11
    clusters.close()

    #7.3.1 ECA MHC1 filtering
    with open("ResultCluster1.txt","w") as resultcluster1:
        resultcluster1.writelines(Clustermenorque11)
    with open('ResultCluster1.txt', 'r') as file:
        content = file.read()
        modified_content = content.replace("-", "")
    with open('ResultCluster1.csv', 'w') as file:
        file.write(modified_content)

    pandascluster1 = pd.read_csv("ResultCluster1.csv", sep = " ")
    pandascluster2 = pandascluster1.filter(["Number","Peptide"])
    pandascluster3 = pandascluster2[(pandascluster2["Number"]<"Consensus")]
    pandascluster4 = pandascluster3[(pandascluster3["Number"]>"1")]
    pandascluster5 = pandascluster4.filter(["Peptide"])
    pandascluster5.to_csv('cluster1.txt',  
                                    header = None, index = None)
    cluster1_ndesejavel = open("cluster1.txt", "r")
    cluster1_subtração = [line.rstrip('\n') for line in open("cluster1.txt")]

    nova_lista_a = [item for item in listafinalepitopes if item not in cluster1_subtração]
    with open("laststep.txt","w") as finalmente1:
        for epitope in nova_lista_a:
            finalmente1.writelines(epitope+"\n")

    #7.3.2 ECA MHC2 filtering
    with open("ResultCluster2.txt","w") as resultcluster2:
        resultcluster2.writelines(Clustermaiorque11)
    with open('ResultCluster2.txt', 'r') as file:
        content = file.read()
        modified_content = content.replace("-", "")
    with open('ResultCluster2.csv', 'w') as file:
        file.write(modified_content)

    pandascluster11 = pd.read_csv("ResultCluster2.csv", sep = " ")
    pandascluster22 = pandascluster11.filter(["Number","Peptide"])
    pandascluster33 = pandascluster22.loc[pandascluster22["Number"] < "Consensus"]
    pandascluster44 = pandascluster33.loc[pandascluster33["Number"] > "1"]
    pandascluster55 = pandascluster44.filter(["Peptide"])
    pandascluster55.to_csv('cluster2.txt',  
                                    header = None, index = None)
    cluster2_ndesejavel = open("cluster2.txt", "r")
    cluster2_subtração = [line.rstrip('\n') for line in open("cluster2.txt")]

    arquivofinalepitopes = open("laststep.txt", "r")
    listafinalmente = [line.rstrip('\n') for line in open("laststep.txt")]

    #7.4 Final epitopes selection after clustering analysis 
    nova_lista_b = [item for item in listafinalmente if item not in cluster2_subtração]
    with open("Your_Final_Epitopes.txt","w") as finalmente2:
        for epitope in nova_lista_b:
            finalmente2.writelines(epitope+"\n")
    
    #8.0 Adding linkers to epitopes   
    nova_lista = []
    nova_lista2 = []
    arquivo = open("Your_Final_Epitopes.txt", "r")
    lista = [line.rstrip('\n') for line in open("Your_Final_Epitopes.txt")]
    for item in lista:
        if len(item) < 11:
            nova_lista.append(Linker1 + item)
    for item2 in lista:
        if len(item2) > 10:
            nova_lista2.append(item2 + Linker2)
    EpitoposFinaisMHCI = len(nova_lista)
    EpitoposFinaisMHCII = len(nova_lista2)
    EpitoposFinaisMHCIs = str(EpitoposFinaisMHCI)
    EpitoposFinaisMHCIIs = str(EpitoposFinaisMHCII)

    print("Os epitopos finais para MHCI e MHCII, já filtrando por clusters de similaridade, são respectivamente " + EpitoposFinaisMHCIs + " e " + EpitoposFinaisMHCIIs)

    # 9.0 Creation of random chimeric models
    num = int(Multi_Chimeric)
    num2 = num - 1
    num3 = int(num2)
    quimera = (">Chimeric_Protein_Model_")
    i = 0
    contador = 0
    mudar = str(contador)
    with open("Chimeric.faa", "w") as novos:
        while contador <= num3:
            contador = contador + 1
            mudar = str(contador)
            random.shuffle(nova_lista)
            StrA = "".join(nova_lista)
            random.shuffle(nova_lista2)
            StrB = "".join(nova_lista2)
            juncao = Adjuvant + StrB + StrA
            print(">CHIMERIC PROTEIN MODEL", mudar,":",".........done", "\n")
            novos.writelines(quimera + mudar + ":\n" + juncao + "\n")
    with open(r'Chimeric.faa', 'r') as meuarq:
        data = meuarq.read()
        data = data.replace(Linker2+Linker1, Linker1)
    with open(r'Chimeric.faa', 'w') as file:
        file.write(data)

    # 9.1 Selection of the chimeric model with the highest antigenicity by VaxignML
    # 9.1.1 VaxignML accesion

    # Função para rodar um comando e capturar a saída
    def run_command(command):
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
        print(result.stderr)

    # Passo 1: Docker Pull
    def docker_pull():
        print("Baixando a imagem Docker...")
        run_command(["docker", "pull", "e4ong1031/vaxign-ml:latest"])

    # Passo 2: Baixar o script VaxignML.sh
    def download_script():
        print("Baixando o script VaxignML.sh...")
        run_command(["wget", "--no-check-certificate" , "https://raw.githubusercontent.com/VIOLINet/Vaxign-ML-docker/master/VaxignML.sh"])

    # Passo 3: Dar permissão de execução no script
    def make_script_executable():
        print("Dando permissão de execução ao script...")
        run_command(["chmod", "a+x", "VaxignML.sh"])

    #Passo 4: executar o vaxignml
    def run_vaxignml_script(input_path, output_path, organism_type):
        try:
            command = ["./VaxignML.sh", input_path, output_path, organism_type]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"VaxignML iniciado com PID: {process.pid}")

            # Espera 2 segundos e verifica se o processo ainda está rodando
            import time
            time.sleep(2)
            
            retcode = process.poll()
            if retcode is None:
                print("O processo ainda está rodando!")
            else:
                print(f"O processo terminou rapidamente com código: {retcode}")
            
        except Exception as e:
            print(f"Erro inesperado: {e}")


    # Caminhos de exemplo (ajuste conforme necessário)
    current_dir = os.getcwd()
    input_fasta = os.path.join(current_dir, "Chimeric.faa")  # Arquivo de entrada (faça o download ou coloque o arquivo desejado)
    output_directory = current_dir  # Diretório de saída
    organism_type = "gram-"  # Tipo de organismo (exemplo: gram-)

    # Execução das etapas
    docker_pull()
    download_script()
    make_script_executable()
    run_vaxignml_script(input_fasta, output_directory, organism_type)
    
    time.sleep(300)

    # Carregar o arquivo TSV
    df = pd.read_csv("Chimeric.result.tsv", sep="\t")

    # Salvar como CSV
    df.to_csv("Chimeric_result.csv", index=False)

    print("Conversão concluída: Chimeric.result.tsv -> Chimeric_result.csv")

    # 9.1.2 Vaxijen proteins filtering

    # 1. Ler e processar o TSV
    VaxFinal = pd.read_csv("Chimeric.result.tsv", sep="\t")
    VaxFinal.columns = VaxFinal.columns.str.strip()  # Remover espaços dos cabeçalhos
    VaxFinal["protegenicity"] = VaxFinal["protegenicity"].astype(float)  # Garantir que seja float

    # 2. Ordenar pelo maior protegenicity
    VaxFinal1 = VaxFinal.sort_values(by="protegenicity", ascending=False)

    # 3. Salvar a amostra com maior protegenicity
    VaxModelName = VaxFinal1[["sample"]]
    VaxModelName.to_csv("Vaxijen.txt", header=False, index=False)

    # 4. Extrair o melhor modelo
    with open("Vaxijen.txt", "r") as vaxi:
        firstlineMODEL = vaxi.readline().strip()
        NameOfTheTopModel = firstlineMODEL.rstrip(":")  # Remove ':' do final

    # 5. Reformatar o arquivo FASTA
    with open("Chimeric.faa", "r") as chimeric_proteins:
        reading_ = chimeric_proteins.read().split(">")

    # 6. Buscar a melhor sequência e salvar
    for protein in reading_:
        if NameOfTheTopModel in protein:
            with open("YourFinalModel.faa", "w") as finalmodel:
                finalmodel.write(f">{protein}")  # Adicionar ">" na frente

    # 7. Ajustar o formato do Chimeric.faa
    with open("Chimeric.faa", "r") as ArrumarQuimeras:
        ArrumarQuimerasBora = ArrumarQuimeras.read().replace("\n>", "\n>\n")

    with open("Chimeric.faa", "w") as ArrumarQuimerasFINALMENTE:
        ArrumarQuimerasFINALMENTE.write(ArrumarQuimerasBora)

    # 8. Remover o arquivo temporário
    os.remove("Vaxijen.txt")


    reading_your_final_model = pd.read_csv("YourFinalModel.faa")
    reading_your_final_model.to_csv("FinalSemCabeca.txt", header=None, index=None)
    with open("FinalSemCabeca.txt") as semcabeca:
        leituradotrem = semcabeca.read()
    
    #10.0 Allertop prediction
    navegadorALLER = webdriver.Firefox(options=firefox_options)
    navegadorALLER.get("https://allercatpro.bii.a-star.edu.sg/")    
    navegadorALLER.find_element(By.XPATH, '//*[@id="seq"]').send_keys(">Multi-epitope\n" + leituradotrem)
    time.sleep(5)
    navegadorALLER.find_element(By.XPATH, '/html/body/center/font/form/input[2]').click()
    time.sleep(5)
    total_height = navegadorALLER.execute_script("return document.body.scrollHeight")
    navegadorALLER.set_window_size(1920, total_height)
    navegadorALLER.save_screenshot("Allertop.png")

    #11.0 ProtParam prediction
    navegadorALLER.get("https://web.expasy.org/protparam/")
    time.sleep(10)    
    navegadorALLER.find_element(By.XPATH, '/html/body/main/div/form/textarea').send_keys(leituradotrem)
    time.sleep(10)
    navegadorALLER.find_element(By.XPATH, '/html/body/main/div/form/input[3]').click()
    time.sleep(10)
    vamoslerisso2 = navegadorALLER.find_element(By.XPATH, '/html/body/main/div/pre[2]')

    vamoslerisso3 = vamoslerisso2.text

    #12.0 PSIPRED prediction
    navegadorALLER.get("http://bioinf.cs.ucl.ac.uk/psipred/")
    time.sleep(10)
    navegadorALLER.find_element(By.XPATH, '//*[@id="id_job_name"]').send_keys("VaxG")
    navegadorALLER.find_element(By.XPATH, '//*[@id="id_email"]').send_keys("bioinformaticsuftm@gmail.com")
    navegadorALLER.find_element(By.XPATH, '//*[@id="id_input_data"]').send_keys(leituradotrem)
    time.sleep(10)
    navegadorALLER.find_element(By.XPATH, '//*[@id="main_form"]/div[6]/input[2]').click()
    time.sleep(10)
    pegarurl = navegadorALLER.current_url

    #13.0 Getting results
    navegadorALLER.close()
    with open("ProtParam.txt","w") as escritadisso1:
        hamescreveisso1 = escritadisso1.writelines(vamoslerisso3)
    with open("PsiPred.txt","w") as escritadisso2:
        hamescreveisso2 = escritadisso2.writelines(pegarurl)


    ###############
    # First Image Generation
    from PIL import Image, ImageDraw, ImageFont 

    with open('Your_Final_Epitopes.txt', 'r') as arquivo:
        lista_epitopos = arquivo.read().splitlines()

    with open('YourFinalModel.faa', 'r') as fasta:
        linhasdofasta = fasta.readlines()

    sequencia_completa = ''.join(linhasdofasta[1:])  # Ignora a primeira linha (cabeçalho)

    # Separação dos epítopos em duas listas: maiores que 11 e menores que 11
    epitopos_maior_11 = [epitopo for epitopo in lista_epitopos if len(epitopo) > 10]
    epitopos_menor_11 = [epitopo for epitopo in lista_epitopos if len(epitopo) < 11]

    # Ordenação dos epítopos maiores que 11 baseando-se na sequência
    lista_epitopos_maior_11_ordenada = sorted(epitopos_maior_11, key=lambda epitopo: sequencia_completa.find(epitopo))

    # Ordenação dos epítopos menores ou iguais a 11 baseando-se na sequência
    lista_epitopos_menor_11_ordenada = sorted(epitopos_menor_11, key=lambda epitopo: sequencia_completa.find(epitopo))

    # Concatenação das listas ordenadas
    listaparaimagem = lista_epitopos_maior_11_ordenada + lista_epitopos_menor_11_ordenada

    # Função para criar a imagem com os epitopos e os linkers
    def criar_imagem_epitopos(partes, adjuvante_texto=""):
        margem = 10 
        altura_retangulo = 50 
        largura_retangulo = 300 

        altura_imagem = (altura_retangulo + margem) * len(partes) + margem
        largura_imagem = largura_retangulo + 2 * margem + 250 

        imagem = Image.new('RGB', (largura_imagem, altura_imagem), 'white')
        draw = ImageDraw.Draw(imagem)

        fonte = ImageFont.truetype("Arial.ttf", 24)

        # Verifica se há adjuvante e define o texto a ser mostrado
        adjuvante_texto = "ADJUVANT" if adjuvantevacina else ""

        if adjuvantevacina:
            # Desenha o retângulo do adjuvante e o texto
            adj_x = margem
            adj_y = margem
            adj_largura = 300
            adj_altura = altura_retangulo
            draw.rectangle([(adj_x, adj_y), (adj_x + adj_largura, adj_y + adj_altura)], fill='green', outline=None)  
            texto_adj_bbox = draw.textbbox((adj_x, adj_y), adjuvante_texto, font=fonte)
            adj_x_texto = adj_x + (adj_largura - texto_adj_bbox[2] + texto_adj_bbox[0]) // 2 
            adj_y_texto = adj_y + (adj_altura - texto_adj_bbox[3] + texto_adj_bbox[1]) // 2  
            draw.text((adj_x_texto, adj_y_texto), adjuvante_texto, fill='white', font=fonte)


        y = margem + altura_retangulo + margem // 2 
        for parte in partes:
            texto_bbox = draw.textbbox((margem, y), parte, font=fonte)
            x_texto = margem + (largura_retangulo - texto_bbox[2] + texto_bbox[0]) // 2
            y_texto = y + (altura_retangulo - texto_bbox[3] + texto_bbox[1]) // 2  

            if len(parte) > 10:
                cor_retangulo = 'navy'
                cor_texto = 'white'
            else:
                cor_retangulo = 'lightcoral'
                cor_texto = 'black'

            draw.rectangle([(margem, y), (largura_retangulo + margem, y + altura_retangulo)], fill=cor_retangulo, outline=None) 
            draw.text((x_texto, y_texto), parte, fill=cor_texto, font=fonte)

            y += altura_retangulo + margem // 2

        tamanho_legenda = 20
        y_legenda = margem
        x_legenda = largura_retangulo + 2 * margem + 50 
        draw.rectangle([(x_legenda, y_legenda), (x_legenda + tamanho_legenda, y_legenda + tamanho_legenda)], fill='navy', outline=None)  
        draw.rectangle([(x_legenda, y_legenda + tamanho_legenda + margem), (x_legenda + tamanho_legenda, y_legenda + 2 * tamanho_legenda + margem)], fill='lightcoral', outline=None)  
        draw.text((x_legenda + tamanho_legenda + 10, y_legenda + (tamanho_legenda - texto_bbox[3] + texto_bbox[1]) // 2), "MHCII epitope", fill='black', font=fonte)
        draw.text((x_legenda + tamanho_legenda + 10, y_legenda + tamanho_legenda + margem + (tamanho_legenda - texto_bbox[3] + texto_bbox[1]) // 2), "MHCI epitope", fill='black', font=fonte)

        imagem.save('sequence.png', dpi=(300, 300), size=(largura_imagem, altura_imagem))


    # Criar a imagem usando a lista2 e o texto do adjuvante
    criar_imagem_epitopos(listaparaimagem, adjuvantevacina)

    

    ###############
    # Second Image Generation
    #Sum of the total value of the epitopes by step
    somatoriadas = pd.read_csv('output.csv')
    somas_colunas = somatoriadas.sum()
    somas_dict = somas_colunas.to_dict()
    MHCIrec = int(somas_dict['MHCI pred'])
    MHCIsec = int(somas_dict['MHCI pred2'])
    MHCIIrec = int(somas_dict['MHCII pred'])
    MHCIIsec = int(somas_dict['MHCII pred2'])
    MHCIrecfiltered = int(somas_dict['MHCI fil1'])
    MHCIsecfiltered = int(somas_dict['MHCI fil2'])
    MHCIIrecfiltered = int(somas_dict['MHCII fil1'])
    MHCIIsecfiltered = int(somas_dict['MHCII fil2'])
    MHCIIrecfiltered = int(somas_dict['MHCII fil1'])
    MHCIover = int(somas_dict['MHCI over1'])
    MHCIIover = int(somas_dict['MHCII over1'])
    MHCIover2 = int(somas_dict['MHCI over2'])
    MHCIIover2 = int(somas_dict['MHCII over2'])
    MHCIfinal = int(EpitoposFinaisMHCI)
    MHCIIfinal = int(EpitoposFinaisMHCII)
    Bcellimage = int(somas_dict['Bcell'])

    #################
    #matplotlib
    import matplotlib.pyplot as plt
    import networkx as nx # type: ignore

    # Criando o grafo direcionado
    G = nx.DiGraph()

    # Adicionando as arestas com suas descrições para MHCI
    edges_mhci = [
        ("MHCI rec", "MHCIrec filtered", {"label": "Filtering"}),
        ("MHCI sec", "MHCIsec filtered", {"label": "Filtering"}),
        ("MHCIrec filtered", "MHCI over", {"label": "Overlapping 1"}),
        ("MHCIsec filtered", "MHCI over", {"label": "Overlapping 1"}),
        ("MHCI over", "MHCIxBc", {"label": "Overlapping 2"}),
        ("MHCIxBc", "MHCI final", {"label": "Cluster and MHCIi"}),
    ]

    G.add_edges_from(edges_mhci)

    # Adicionando o nó Bcell abaixo de MHCIxBc e MHCIIxBc
    edges_mhci.append(("MHCIxBc", "Bcell", {"label": "Overlapping 2"}))
    edges_mhci.append(("MHCIIxBc", "Bcell", {"label": "Overlapping 2"}))

    # Adicionando as arestas com suas descrições para MHCII
    edges_mhcii = [
        ("MHCII rec", "MHCIIrec filtered", {"label": "Filtering"}),
        ("MHCII sec", "MHCIIsec filtered", {"label": "Filtering"}),
        ("MHCIIrec filtered", "MHCII over", {"label": "Overlapping 1"}),
        ("MHCIIsec filtered", "MHCII over", {"label": "Overlapping 1"}),
        ("MHCII over", "MHCIIxBc", {"label": "Overlapping 2"}),
        ("MHCIIxBc", "MHCII final", {"label": "Cluster"}),
    ]

    G.add_edges_from(edges_mhcii)

    # Adicionando as arestas ao grafo
    G.add_edges_from(edges_mhci)

    # Definindo a posição dos nós no diagrama com maior espaçamento
    pos = {
        "MHCI rec": (1, 10),
        "MHCI sec": (1, 5),
        "MHCIrec filtered": (5, 10),
        "MHCIsec filtered": (5, 5),
        "MHCI over": (9, 7.5),
        "MHCIxBc": (13, 7.5),
        "MHCI final": (17, 7.5),
        "MHCII rec": (1, -5),  # Posição mais baixa para MHCII
        "MHCII sec": (1, -10),  # Posição mais baixa para MHCII
        "MHCIIrec filtered": (5, -5),  # Posição mais baixa para MHCII
        "MHCIIsec filtered": (5, -10),  # Posição mais baixa para MHCII
        "MHCII over": (9, -7.5),  # Posição mais baixa para MHCII
        "MHCIIxBc": (13, -7.5),  # Posição mais baixa para MHCII
        "MHCII final": (17, -7.5),  # Posição mais baixa para MHCII
        "Bcell": (7, 0),  # Posição centralizada entre MHCIxBc e MHCIIxBc
    }

    # Desenhando os nós com tamanho maior
    nx.draw_networkx_nodes(G, pos, nodelist=["MHCI rec", "MHCI sec", "MHCIrec filtered", "MHCIsec filtered", "MHCI over", "MHCIxBc", "MHCI final"], node_color='skyblue', node_size=5000)
    nx.draw_networkx_nodes(G, pos, nodelist=["MHCII rec", "MHCII sec", "MHCIIrec filtered", "MHCIIsec filtered", "MHCII over", "MHCIIxBc", "MHCII final"], node_color='lightcoral', node_size=5000)
    nx.draw_networkx_nodes(G, pos, nodelist=["Bcell"], node_color='lightgreen', node_size=6000)

    # Desenhando as arestas com maior comprimento
    nx.draw_networkx_edges(G, pos, arrowsize=20, connectionstyle='arc3,rad=0.1')

    # Adicionando as descrições dos nós externamente
    for node, (x, y) in pos.items():
        plt.text(x, y + 2.2, node, ha='center', va='center', fontsize=12, fontweight='bold', color='black')

    # Adicionando as descrições das arestas
    edge_labels_mhci = {(source, target): data["label"] for (source, target, data) in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_mhci, font_color='red', label_pos=0.5, font_size=8)

    # Adicionando valores dentro dos nós
    node_values = {
        "MHCI rec": str(MHCIrec),
        "MHCI sec": str(MHCIsec),
        "MHCIrec filtered": str(MHCIrecfiltered),
        "MHCIsec filtered": str(MHCIsecfiltered),
        "MHCI over": str(MHCIover),
        "MHCIxBc": str(MHCIover2),
        "MHCI final": str(MHCIfinal),
        "MHCII rec": str(MHCIIrec),
        "MHCII sec": str(MHCIIsec),
        "MHCIIrec filtered": str(MHCIIrecfiltered),
        "MHCIIsec filtered": str(MHCIIsecfiltered),
        "MHCII over": str(MHCIIover),
        "MHCIIxBc": str(MHCIIover2),
        "MHCII final": str(MHCIIfinal),
        "Bcell": str(Bcellimage),
    }

    # Mostrando os valores dentro dos nós
    for node, value in node_values.items():
        plt.text(pos[node][0], pos[node][1], value, ha='center', va='center', fontsize=17, fontweight='bold', color='black')

    plt.title("Flowchart - MHCI and MHCII")
    plt.axis('off')  # Desativando os eixos
    plt.gcf().set_facecolor('white')  # Definindo o fundo branco
    plt.gcf().set_size_inches(12, 10)  # Ajustando o tamanho da imagem
    plt.tight_layout()  # Garantindo um layout ajustado
    plt.savefig("flowchart.png", format="png", dpi=300)  # Salvando a imagem como PNG com 300 DPI



    ### ZIPPING mhcintermediaries files
    caminho_pasta_atual = os.getcwd()
    nome_arquivo_zip = "MHCintermediariesFILES.zip"

    with zipfile.ZipFile(nome_arquivo_zip, 'w') as arquivo_zip:
        for nome_arquivo in os.listdir(caminho_pasta_atual):
            if nome_arquivo.startswith("MHC"):
                caminho_completo = os.path.join(caminho_pasta_atual, nome_arquivo)
                arquivo_zip.write(caminho_completo, nome_arquivo)

    #Saving the results into one zip file
    z = zipfile.ZipFile('Final.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('Allertop.png')
    z.write('Chimeric.faa')
    z.write('ProtParam.txt')
    z.write('PsiPred.txt')
    z.write('Your_Final_Epitopes.txt')
    z.write('YourFinalModel.faa')
    z.write('Chimeric_result.csv')
    z.write('sequence.png')
    z.write('flowchart.png')
    z.write('output.csv')
    z.close()
    
    return redirect('/recebidos/')
