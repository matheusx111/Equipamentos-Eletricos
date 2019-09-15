import pandas as pd
import numpy as np
from planilhas import Planilha

planilhas = Planilha() 
tab421 = planilhas.tabela(sheet_name = "4.21")
tab421 = tab421.replace({'Cabo isolado em XLPE':'XLPE', 'Cabo isolado em EPR':'EPR'})
tab42 = planilhas.tabela(sheet_name = "4.2")
tab46 = planilhas.tabela(sheet_name = "4.6")
tab47 = planilhas.tabela(sheet_name = "4.7")
tab48 = planilhas.tabela(sheet_name = "4.8")


class Condutor():
    """Parâmetros: 
            material_isolante : string
                Uma string que informa o tipo do material isolante: XLPE, EPR.

            tipo_condutor : string
                Uma string que informa o material do condutor: "Fio de alumínio duro"; 
                    "Fio de cobre duro"; "IACS – padrão internacional de cobre recozido"; 
                    "Zincado para alma de cabos de alumínio".

            fator_secao_tensao : string ou numero
                Um número para a seção do condutor, para a classe de tensão "8.7kV - 15kV";
                    para classes de tensão diferentes, inserir o número para a seção do condutor + ".1", ex: "300.1"."""
    def __init__(self, material_isolante, tipo_condutor, fator_secao_tensao, fator_diametro, tensao_linha):

        self.material_isolante = material_isolante
        self.tipo_condutor = tipo_condutor
        self.fator_secao_tensao = fator_secao_tensao
        self.fator_diametro = fator_diametro
        self.tensao_fase = tensao_linha / np.sqrt(3)

    def gradiente_potencial(self, e_is, e_imp, tensao_fase, B, Rc, A):
        """ ---- Função para calcular o gradiente de potencial ----
        Primeiro argumento é a tensão de fase; Segundo argumento é o raio do condutor; Terceiro argumento é a distância B;
        Quarto argumento é a espessura da camada isolante; Quinto argumento é a constante dielétrica do material isolante;
        último argumento é a constante dielétrica da impureza"""

        # Variável que armazena o valor do gradiente de potencial
        Vb = (0.869 * (e_is / e_imp) * self.tensao_fase) / ((B + Rc) * np.log((Rc + A) / Rc))

        return Vb

    def raio_condutor(self):

        """ ---- Função que retorna o raio do condutor em mm ----
        Primeiro argumento é to tipo string que fornece o material isolante;
        Segundo argumento é um fator diâmetro e nive de tensão para a tabela 4.21"""
        
        # Variável que armazena o valor do raio do condutor após buscar na tabela
        Rc = (1/2) * tab421.loc[tab421['Tipo de isolação'] == self.material_isolante].loc[tab421['Caracteristica']
                                                                                    == 'Diâmetro do condutor - mm', [self.fator_secao_tensao]].values[0,0]
        return Rc

    def distancia_B(self):

        """ ---- Função que retorna a distância entre o ponto considerado no interior da isolação e a superfície do
        condutor, em mm; ----
        Primeiro argumento é to tipo string que fornece o material isolante;
        Segundo argumento é um fator diâmetro e nive de tensão para a tabela 4.21"""

        # Variável que armazena da distância B após buscar na tabela
        B = (1/2) * tab421.loc[tab421['Tipo de isolação'] == self.material_isolante].loc[tab421['Caracteristica']
                                                                                    == 'Espessura da isolação -mm', [self.fator_secao_tensao]].values[0,0]
        return B

    def espessura_camada_isolante(self):

        """ ---- Função que retorna a espessura da camada isolante, em mm; ----
        Primeiro argumento é to tipo string que fornece o material isolante;
        Segundo argumento é um fator diâmetro e nive de tensão para a tabela 4.21"""

        # Variável que armazena o valor da espessura da isolação após buscar na tabela
        A = tab421.loc[tab421['Tipo de isolação'] == self.material_isolante].loc[tab421['Caracteristica']
                                                                            == 'Espessura da isolação -mm', [self.fator_secao_tensao]].values[0,0]

        return A

    def funcao_constante_dieletrica_isolante(self):

        """ ---- Função que retorna a constante dieletrica do material isolante; ----
        Primeiro argumento é do tipo string que fornece o material isolante;"""

        # Variável que armazena o valor da constante dielétrica do material isolante após buscar na tabela
        constante_dieletrica_isolante = tab46.loc[tab46['Materiais Isolantes'] == self.material_isolante, [
            'ε']].values[0,0]

        return constante_dieletrica_isolante

    def funcao_constante_dieletrica_impureza(self, material_impureza):

        """ ---- Função que retorna a constante dieletrica da impureza; ----
        Primeiro argumento é to tipo string que fornece o material isolante;"""

        # Variável que armazena o valor da constante dielétrica da impureza após buscar na tabela
        constante_dieletrica_impureza = tab46.loc[tab46['Materiais Isolantes'] == material_impureza, [
            'ε']].values[0,0]

        return constante_dieletrica_impureza

    def capacitancia_cabo(self, Dc, A, Ebi):

        """ ---- Função que calcula a caácitância do cabo, em (micro F / km) ----
        Primeito argumento é o diâmetro do condutor; Segundo argumento é a espessura da camada isolante;
        Terceiro argumento é a espessura da blindagem interna; Quarto argumento é o tipo do material isolante"""

        # Variável que armazena o valor do diâmetro sobre a isolação do material isolante
        Dsi = Dc + 2 * A + 2 * Ebi
        # Variável que recebe o valor da constante dielétrica do material
        constante_dieletrica_isolante = self.funcao_constante_dieletrica_isolante()
        # Variável que armazena o valor da capacitância calculada
        C = (0.0556 * constante_dieletrica_isolante) / (np.log(Dsi / (Dc + 2 * Ebi)))

        return C

    def perdas_dieletricas(self, C):
        """ ---- Função que calcula as perdas dielétricas do cabo, em W/m ----
        Primeiro argumento é a capacitância do cabo; Segundo argumento é a tensão de fase do sistema;
        Terceiro argumento é o tipo do material isolante"""

        tangente_delta = tab46.loc[tab46['Materiais Isolantes']
                                == self.material_isolante, ['tg δ (20ºC)']].values[0,0]

        Pd = 0.3769 * C * (self.tensao_fase**2) * tangente_delta

        return Pd

    def perda_dieletrica_total(self, Pd, comprimento):
        """ ---- Função que calcula as perdas totais dielétricas do cabo, em W----
        Primeiro argumento é as perdas dielétricas; Segundo argumento é o comprimento do cabo"""

        Pdt = Pd * comprimento

        return Pdt

    def diametro_externo(self):
        """ ---- Função que retorna o diâmetro externo, em mm; ----
        Primeiro argumento é to tipo string que fornece o material isolante;
        Segundo argumento é um fator diâmetro e nivel de tensão para a tabela 4.21"""

        Dca = tab421.loc[tab421['Tipo de isolação'] == self.material_isolante].loc[tab421['Caracteristica']
                                                                            == 'Diâmetro externo - mm', [self.fator_secao_tensao]].values[0,0]

        return Dca

    def fator_K(self, fator, encordoamento, fator_diametro):

        if fator_diametro != 0:
            K = tab47.loc[tab47['Fator'] == fator].loc[tab47['Condutor'] == encordoamento, [fator_diametro]].values[0,0]
        else:
            K = tab47.loc[tab47['Fator'] == fator].loc[tab47['Condutor'] == encordoamento, ['Unnamed: 2']].values[0,0]

        return K

    def resistencia_cc(self, K1, K2, K3, p20, a20, Tc, S):
        """ ---- Função que calcula a resistência à corrente contínua a T°C, em mΩ/m ----
        Primeiro argumento é o fator K1; Segundo argumento é o fator K2; Terceito argumento é o fator K3;
        Quarto argumento é a resistividade; Quinto argumento é o coeficiente de temperatura do material do condutor;
        Sexto argumento é a temperatura do condutor, em °C; último argumento é a seção do condutor, em mm²"""

        Rcc = (1/S) * (1000 * K1 * K2 * K3 * p20) * (1 + a20 * (Tc - 20))

        return Rcc

    def componente_correcao_efeito_peculiar(self, Rcc):
        """ ---- Função que calcula a componente que corrige o efeito pelicular da distribuição de corrente na seção
        do condutor ----
        Primeiro argumento é a resistência à corrente contínua"""

        Fs = 0.15 / Rcc
        Ys = (Fs**2) / (192 + 0.8 * (Fs**2))

        return Ys

    def componente_correcao_proximidade_cabos(self, Ys, Dc, Dmg):
        """ ---- Função que calcula a componente que corrige o efeito de proximidade entre os cabos ----
        Primeiro argumento é a componente que corrige o efeito peculiar;
        Segundo argumento é o diâmetro do condutor; Terceiro argumento é o diâmetro médio geométrico"""

        Yp = Ys * ((Dc / Dmg)**2) * ((1.18 / (0.27 + Ys)) + 0.312 * ((Dc / Dmg)**2))

        return Yp

    def calcular_Dmg(self, D):
        """ ---- Função que calcula o diâmetro médio geométrico ----
        Primeiro argumento é a distância que separa os cabos"""

        return 1.26 * D

    def resistividade_condutor(self):
        """ --- Função que retorna a resistividade do condutor ----
        Primeiro argumento é o tipo do condutor"""

        resistividade = tab42.loc[tab42['Especificações'] ==
                                'Resistividade máxima a 20ºC (Ω/mm2/m)', [self.tipo_condutor]].values[0,0]

        return resistividade

    def coeficiente_temperatura(self):
        """ --- Função que retorna o coeficiente de temperatura do condutor ----
        Primeiro argumento é o tipo do condutor"""

        coeficiente_temperatura = tab42.loc[tab42['Especificações'] ==
                                            'Coeficiente de variação da resistência/ºC a 20ºC', [self.tipo_condutor]].values[0,0]
        return coeficiente_temperatura

    def reatancia_positiva(self, Dmg, Dc):
        """ ---- Função que calcula a reatância positiva ----
        Primeiro argumento é a distância média geométrica; Segundo argumento é o diâmetro do condutor"""

        Xp = 0.0754 * np.log((Dmg) / (0.779 * (Dc / 2)))

        return Xp

    def reatancia_blindagem1(self, Dmg, Dmb):
        """ ---- Função que calcula a reatância da blindagem para um ponto de aterramento ----
        Primeiro argumento é a distância média geométrica; Segundo argumento é o diâmetro médio da blindagem"""

        Xb = 0.0754 * np.log((2 * Dmg) / (Dmb))

        return Xb

    def acrescimo_componente_resistivo(self, Rb, Xb):
        # """ ---- Função que calcula o acréscimo ao componente resistivo da impedância de sequência positiva ----
        #     Primeiro argumento é a resistência da blindagem; Segundo argumento é a reatância da blindagem""""

        delta_Rb = Rb / (((Rb / Xb)**2) + 1)

        return delta_Rb

    def resistencia_blindagem(self, coeficiente_temp, resistividade, Sb, Tb, K4):
        """ ---- Função que calcula a resistência da blindagem ----
            Primeiro argumento é o coeficiente de temperatura; Segundo argumento é a resistividade
            Terceiro argumento é a área da seção traversal; Quarto argumento é a temperatura da blindagem;
            Último argumento é a constante K4"""

        Rb = (1 + coeficiente_temp * (Tb - 20)) * (1000 * K4 * resistividade) / Sb

        return Rb

    def secao_blindagem(self, diametro_fio, intensidade_corrente):
        """ ---- Função que retorna a seção da blindagem ----
            Primeiro argumento é o diâmetro do fio; Segundo argumento é a intensidade da corrente que passa no fio"""

        Sb = tab48.loc[tab48['Diâmetro dos fios em mm'] == diametro_fio].loc[tab48['Intensidade máx. adm. em curto-circuito (1s) kA'] == intensidade_corrente, [
            'Seção da blindagem (mm²)']].values[0, 0]

        return Sb

    def reducao_indutancia(self, M, Rb, Xb):
        """ ---- Função que calcula a redução da indutância de sequência positiva ----
            Primeiro argumento é a resistência da blindagem; Segundo argumento é a reatância da blindagem à um ponto de aterramento"""

        delta_Lb = ((M) / (((Rb / Xb)**2) + 1))

        return delta_Lb

    def reducao_reatancia_positiva(self, Rb, Xb):
        """ ---- Função que calcula a redução da reatância de sequência positiva ----
            Primeiro argumento é a resistência da blindagem; Segundo argumento é a reatância da blindagem à um ponto de aterramento"""

        delta_Xb = ((Xb) / (((Rb / Xb)**2) + 1))

        return delta_Xb

    def reatancia_blindagem2(self, Dmg, Dmb):
        """ ---- Função que calcula a reatância da blindagem para varios pontos de aterramento ----
            Primeiro argumento é a distância média geométrica; Segundo argumento é a diâmetro médio da blindagem"""

        Xb = 0.0754 * np.log((2 * Dmg) / (Dmb))

        return Xb

    def diametro_medio_bindagem(self, Dc, Ei, Ebi, Ebe, Ebm):
        """ ---- Função que calcula o diâmetro médio da blindagem  ----
            Primeiro argumento é o diâmetro do condutor; Segundo argumento é a espessura da isolação;
            Terceiro argumento é a espessura da blindagem do interna; Quarto argumento é a espessura da blindagem externa;
            Último argumento é a espessura da blindagem metálica"""

        Dmb = Dc + 2 * Ei + 2 * Ebi + 2 * Ebe + (Ebm / 2)

        return Dmb

    def resistencia_positiva(self, Dmg, Dc, fator_diametro):
        """ ---- Função que calcula a resistência positiva ----"""
        
        K1 = self.fator_K('K1', 'Fio ou encordoamento compacto', fator_diametro)
        K2 = self.fator_K('K2', 'Fio ou encordoamento compacto', 0)
        K3 = self.fator_K('K3', 'Cabos singelos', 0)
        p20 = self.resistividade_condutor()
        a20 = self.coeficiente_temperatura()
        Tc = 90  # teste
        S = 300
        Rcc = self.resistencia_cc(K1, K2, K3, p20, a20, Tc, S)
        Ys = self.componente_correcao_efeito_peculiar(Rcc)
        Yp = self.componente_correcao_proximidade_cabos(Ys, Dc, Dmg)
        Rp = Rcc * (1 + Ys + Yp)

        return Rp

    def reatancia_positiva_efetiva(self, Xp, delta_Xb):
        """ ---- Função que calcula a reatância positiva efetiva para varios pontos de aterramento ----
            Primeiro argumento é a reatância positiva para varios pontos de aterramento;
            último argumento é a redução da reatância positiva"""

        Xf = Xp - delta_Xb

        return Xf

    def resistencia_positiva_efetiva(self, Rp, delta_Rb):
        """ ---- Função que calcula a resistência positiva efetiva para varios pontos de aterramento ----
            Primeiro argumento é a resistência positiva para varios pontos de aterramento;
            último argumento é o acréscimo da resistência positiva"""

        Rf = Rp + delta_Rb

        return Rf

    def impedancia_positiva_um_ponto(self, fator_diametro):
        """ ---- Função que calcula a impedância positiva para apenas um ponto de aterramento, "(m Ohms) / m" ----

        Return:     Um float complexo"""

        Dc = 2 * self.raio_condutor()
        Dca = self.diametro_externo()
        D = Dca  # teste
        Dmg = self.calcular_Dmg(D)
        Rp = self.resistencia_positiva(Dmg, Dc, fator_diametro)
        Xp = self. reatancia_positiva(Dmg, Dc)
        Zp = np.complex(Rp, Xp)

        return Zp

    def impedancia_positiva_aterrada_pontos(self, Rpf, Xpf):
        """ ---- Função que calcula a impedância positiva para vários pontos de aterramento ----
            Primeiro argumento é a resistência efetiva positiva; Segundo argumento é a reatância efetiva positiva"""

        Zpf = np.complex(Rpf, Xpf)

        return Zpf
