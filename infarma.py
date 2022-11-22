from PyQt5 import uic,QtWidgets,QtGui,QtCore
import pyodbc
import hashlib
import configparser
import logging
from datetime import date,datetime



def data_atual():
  """Retorna data atual"""
  return str(date.today().strftime("%d%m%y"))

def date_time():
  """Retorna data e hora atual"""
  return str(datetime.today().strftime("%d/%m/%Y  %H:%M:%S"))

#Cria log
log_format = '%(asctime)'
logging.basicConfig(filename='infarmaBal'+data_atual()+'.log',filemode='a',level=logging.INFO)
logger=logging.getLogger('root')


#inicializacao das interfaces graficas
app=QtWidgets.QApplication([])
telaLogin=uic.loadUi("loginInfarma.ui")
telaPrincipal=uic.loadUi("telaPrincipal.ui")
telaProdutIns=uic.loadUi("telaProdutIns.ui")
telaNotif=uic.loadUi("notification.ui")
telaRemov=uic.loadUi("telaAtencao.ui")
telaUpdate=uic.loadUi("telaProdutUpd.ui")
telaPrincipal.tableWidget.setColumnWidth(0,110)
telaPrincipal.tableWidget.setColumnWidth(1,525)
telaPrincipal.tableWidget.setColumnWidth(2,140)
telaPrincipal.tableWidget.setColumnWidth(3,100)
telaPrincipal.tableWidget.setColumnWidth(4,110)
telaProdutIns.lineEditCodProdut.setValidator(QtGui.QDoubleValidator())
telaProdutIns.lineEditQtd.setValidator(QtGui.QIntValidator())
telaPrincipal.lineEditCodBal.setValidator(QtGui.QIntValidator())

cachedRemove = [0,0,0,0,0]
cachedUpdate = [0,0,0,0,0,0]


#Leitura do arquivo ini
try:
    cfg = configparser.ConfigParser()
    cfg.read('Infarma.ini')
    cod_loja=cfg.getint('SERVIDOR','Loja')
    hostName=cfg.get('SERVIDOR','HostName')
    dataBase=cfg.get('SERVIDOR','Database')
    driverOdbc='{SQL Server}'
    telaLogin.labelDataCon.setText(f'{hostName} / {dataBase} - LOJA: {cod_loja}')
except Exception as e:
    logging.info('Erro na leitura do arquivo Infarma.ini')
    logging.warning(date_time()+e)


#realiza conexão com o banco
try:
    conn = pyodbc.connect(f'DRIVER={driverOdbc};SERVER={hostName};DATABASE={dataBase};UID=**;PWD=**;')
except Exception as e:
    logging.warning(date_time()+e)
    telaLogin.labelInfoLogin.setText('')
finally:
    conn.close()


#Funções DB
def connect_db():
    """Realiza a conexão com o banco e retorna a mesma"""
    try:
        conn = pyodbc.connect(f'DRIVER={driverOdbc};SERVER={hostName};DATABASE={dataBase};UID=VMDApp;PWD=VMD22041748;')
        return conn
    except Exception as e:
        s = 'Erro connect_db'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)

def add_produt(cod_loja,cod_bal,cod_produt,cod_lote,qtd_produt,dat_vctlot):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = (f"Insert Into BALIT (Cod_Loja,Num_SeqBal,Cod_Produt,Cod_Lote,Cod_Local,Num_Contag,Qtd_Produt,Dat_VctLot) Values ({cod_loja},{cod_bal} ,{cod_produt}, '{cod_lote}', 1, 1, {qtd_produt}, '{dat_vctlot}')")
        cursor.execute(sql)
        cursor.commit()
        refreshList(cod_bal)
        
        return
    except Exception as e:
        s = 'Erro add_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cursor.close()
        conn.close()

def update_produt(cod_loja,cod_bal,cod_produt,cod_lote,qtd_produt,dat_vctlot,cod_lote_new):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = (f"UPDATE BALIT  SET Qtd_Produt = {qtd_produt}, Dat_VctLot = '{dat_vctlot}', Cod_Lote = {cod_lote_new} WHERE Cod_Loja = {cod_loja} AND Num_SeqBal = {cod_bal} AND Cod_Produt = {cod_produt} AND Cod_Lote = '{cod_lote}' AND Cod_Local = 1 AND Num_Contag = 1")
        cursor.execute(sql)
        cursor.commit()
        refreshList(cod_bal)
        sair_update_produt()
        cachedUpdate= []

        
        return
    except Exception as e:
        s = 'Erro update_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cursor.close()
        conn.close()
        
def delete_produt(cod_loja,cod_bal,cod_produt,cod_lote):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = (f"DELETE FROM BALIT WHERE Cod_Loja = {cod_loja} AND Num_SeqBal = {cod_bal} AND Cod_Produt = {cod_produt} AND Cod_Lote = '{cod_lote}' AND Cod_Local = 1 AND Num_Contag = 1")
        cursor.execute(sql)
        cursor.commit()
        refreshList(cod_bal)
        print('DELETE')
        refreshList(cod_bal)
        sair_remove_produt()

        return
    except Exception as e:
        s = 'Erro delete_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cachedRemove = [0,0,0,0,0]
        cursor.close()
        conn.close()

def consulta_produt_balit(cod_produt,cod_lote, cod_bal):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = (f"SELECT 1 FROM BALIT WHERE Cod_Produt= {cod_produt}  AND Cod_Lote='{cod_lote}' AND Num_SeqBal={cod_bal} AND Cod_Loja={cod_loja}")
        cursor.execute(sql)
        result = cursor.fetchall()
        if result == []:
            is_valid = True
            print(date_time()+'Valido -Consulta Produto Balit')
            return is_valid
            
        else:
            is_valid = False
            print(date_time()+'Inalido -Consulta Produto Balit')
            return is_valid
    except Exception as e:
        s = 'Erro consulta_produt_balit'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cursor.close()
        conn.close()

def consulta_produt(cod_produt):
    result = []
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = (f"Select Cod_Produt, Des_Produt, Ctr_Venda   From PRODU   Where Cod_Produt = {cod_produt} or Cod_Ean ='{cod_produt}'")
        cursor.execute(sql)
        result=cursor.fetchall()
        return result
    except Exception as e:
        s = 'Erro consulta_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
        return result
    finally:
        cursor.close()
        conn.close()

def list_produt(cod_bal):
    """Gera lista de produtos do balanço"""
    try:        
        sql = (f'SELECT P.Cod_Produt, P.Des_Produt,B.Cod_Lote,B.Qtd_Produt,CONVERT(VARCHAR,B.Dat_VctLot, 103) FROM BALIT B INNER JOIN PRODU P ON B.Cod_Produt=P.Cod_Produt WHERE Num_SeqBal={cod_bal}')
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        s = 'Erro list_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cursor.close()
        conn.close()

def consulta_bal():
    """Consulta balanço no banco de dados"""
    
    try:
        conn=connect_db()
        cursor=conn.cursor()
        cod_bal=str(telaPrincipal.lineEditCodBal.text()) 
        sql = (f'select Tip_Balanc, Flg_Proces,convert(varchar, Dat_Balanc, 103) from BALCB where Cod_Loja   = {cod_loja}  and Num_SeqBal = {cod_bal}')
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        s = 'Erro consulta_bal'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)


#Funções Validação
def valida_login():
    """Valida os dados de login"""
    telaLogin.labelInfoLogin.setText('')
    conn = connect_db()    
    cursor=conn.cursor()

    try:
        text_login = str(telaLogin.lineEditUser.text())
        text_senha = str(telaLogin.lineEditPassword.text()) 
        text_login = text_login.upper()
        text_senha = text_senha.upper()
        text_senha = text_senha.encode()

        #gerando hash md5 da senha
        hash= hashlib.md5(text_senha)
        snh_hash=hash.hexdigest()

        sql=(f"SELECT 1 FROM USUAR WHERE Nom_Login='{text_login}' AND Snh_Hash='{snh_hash}' AND Flg_Bloque=0")
        cursor.execute(sql)
        result = cursor.fetchall()
        
        if result!=[]:
            telaLogin.close()
            return telaPrincipal.show() 
        else:
            telaLogin.labelInfoLogin.setText('Usuário ou senha inálidos')    
    except Exception as e:
        s = 'Erro valida_login'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
    finally:
        cursor.close()
        conn.close()

def valida_cod_bal():
    
    try:
        cod_bal=int(telaPrincipal.lineEditCodBal.text()) 
        if cod_bal == '':
            text_on = 'Por favor preencha'
            text_two = 'código do balanço.'
            tela_notif(text_on,text_two)
            return
        elif type(cod_bal) != int :
            text_on = 'Por favor preencha um'
            text_two = 'código de balanço válido.'
            tela_notif(text_on,text_two)
            
            return
        else:
            try:
                
                result = consulta_bal()
                print(result)
                if result == []:
                    text_on = 'Balanço não encontrado'
                    text_two = 'confira o código do balanço.'
                    tela_notif(text_on,text_two)
                    return
                elif result[0][1] != False:
                    text_on = 'Este balanço já foi processado.'
                    text_two = ''
                    tela_notif(text_on,text_two)
                    return
                elif str(result[0][0]) != 'T':
                    text_on = 'Este balanço não é'
                    text_two = 'do tipo "Total".'
                    tela_notif(text_on,text_two)
                    return
                elif str(result[0][0]) == 'T' and result[0][1] == False:
                    telaPrincipal.lineEditContBal.setText(str(result[0][2]))
                    telaPrincipal.lineEditCodBal.setStyleSheet("""
                                                                    border:2px solid rgb(204, 204, 204);
                                                                    border-radius:4px;
                                                                    background-color: rgb(238, 238, 238);""")
                    telaPrincipal.lineEditCodBal.setReadOnly(True)
                    telaPrincipal.btnAdd.setEnabled(True)
                    telaPrincipal.lineEditCodBal.setEnabled(False)
                    refreshList(cod_bal)
                    return
            except Exception as e:
                s = 'Erro valida_cod_bal_sub'
                logging.warning(date_time()+s)
                logging.warning(date_time()+e)
                
            


    except Exception as e:
        text_on = 'Por favor, preencha um'
        text_two = 'código válido.'
        tela_notif(text_on,text_two)
        s = 'Erro valida_cod_bal'
        logging.warning(date_time()+s)
        return
      
def valida_codprodut():
    try:
        cod_produt = int(telaProdutIns.lineEditCodProdut.text()) 
        if cod_produt == '':
            text_on = 'Por favor preencha o código do produto.'
            text_two = ''
            tela_notif(text_on,text_two)
            return
        else:
            result = consulta_produt(cod_produt)
            if result != []:
                telaProdutIns.lineEditDesc.setText(result[0][1])
                if str(result[0][2]) == 'L':
                    text_on = 'Este produto é do tipo "Livre".'
                    text_two = ''
                    tela_notif(text_on,text_two)
                    return
                else:
                    telaProdutIns.lineEditQtd.setEnabled(True)
                    telaProdutIns.lineEditLote.setEnabled(True)
                    telaProdutIns.dateEditVenc.setEnabled(True)
                    telaProdutIns.btnAplic.setEnabled(True)
                    telaProdutIns.lineEditQtd.setFocus()
                    return
                
            else:
                text_on = 'Produto não cadastrado.'
                text_two = ''
                tela_notif(text_on,text_two)
                return
    except Exception as e:
        s = 'Erro valida_codprodut'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)

def valida_produt():
    try:
        cod_bal= int(telaPrincipal.lineEditCodBal.text()) 
        cod_produt = int(telaProdutIns.lineEditCodProdut.text()) 
        qtd_produt = int(telaProdutIns.lineEditQtd.text()) 
        cod_lote = str(telaProdutIns.lineEditLote.text()) 
        dat_vctlot = str(telaProdutIns.dateEditVenc.text())
        print(date_time()+'Valida Produto') 
        is_valid = consulta_produt_balit(cod_produt,cod_lote,cod_bal)

        if is_valid is True:
            print(date_time()+'Valido Produto - Valido')
            add_produt(cod_loja,cod_bal,cod_produt,cod_lote,qtd_produt,dat_vctlot)
        else:
            text_on = 'Produto já inserido no balanço'
            text_two = 'com esse lote.'
            print(date_time()+'Valido Produto Invalido')
            tela_notif(text_on,text_two)
            
            
            return


        

    except Exception as e:
        s = 'Erro valida_produt'
        logging.warning(date_time()+s)
        logging.warning(e)

def removeProdut():
    try:
        
        #cod_bal= int(telaPrincipal.lineEditCodBal.text()) 
        cachedRemove[0] = (int(telaPrincipal.lineEditCodBal.text()) )
        #cod_produt=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
        cachedRemove[1]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
        #des_produt=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(1).data()
        cachedRemove[2]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(1).data()
        #cod_lote=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(2).data()
        cachedRemove[3]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(2).data()
        telaRemov.label_2.setText(f'{cachedRemove[1]} - {cachedRemove[2]} | {cachedRemove[3]}')
        telaRemov.show()
        #on_remove(cod_loja,cod_bal,cod_produt,des_produt,cod_lote)
        
    except Exception as e:
        s = 'Erro remove_produt'
        logging.warning(date_time()+s)
        logging.warning(e)
        
def on_remove():
    try:
        if cachedRemove[0] != 0:
            cod_bal = cachedRemove[0]
            cod_produt = cachedRemove[1]
            cod_lote = cachedRemove[3]
            delete_produt(cod_loja,cod_bal,cod_produt,cod_lote)
           


        else:
            print('Erro 2.1')
            return
        

    except Exception as e:
        s = 'Erro on_remove'
        logging.warning(date_time()+s)
        logging.warning(e)

def editProdut():
    try:
        
        #cod_bal
        cachedUpdate[0] = (str(telaPrincipal.lineEditCodBal.text()) )
        #cod_produt
        cachedUpdate[1]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
        #des_produt
        cachedUpdate[2]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(1).data()
        #cod_lote
        cachedUpdate[3]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(2).data()
        #qtd_produt
        cachedUpdate[4]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(3).data()
        #dat_vctlot
        cachedUpdate[5]=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(4).data()
        
        
        telaUpdate.lineEditCodProdut.setText(str(cachedUpdate[1]))
        telaUpdate.lineEditDesc.setText(str(cachedUpdate[2]))
        telaUpdate.lineEditQtd.setText(str(cachedUpdate[4]))
        telaUpdate.lineEditLote.setText(str(cachedUpdate[3]))
        # dataVencimento = (cachedUpdate[5])
        # vct_year = (dataVencimento[6:10])
        # vct_month = (dataVencimento[3:5])
        # vct_day = (dataVencimento[0:2])
        # dataVct = (f'{vct_year}{vct_month}{vct_day}')
        # dataAtual = date(dataVct)
        
        # print(dataAtual)
        # telaUpdate.dateEditVenc.setDate(dataAtual)
        # print(cachedUpdate[5])
        telaUpdate.show()
        #on_remove(cod_loja,cod_bal,cod_produt,des_produt,cod_lote)
        #od_loja,cod_bal,cod_produt,cod_lote,qtd_produt,dat_vctlot)
    except Exception as e:
        s = 'Erro edit_produt'
        logging.warning(date_time()+s)
        logging.warning(e)
        
def on_update():
    try:
        if cachedUpdate[0] != 0:
            cod_bal = cachedUpdate[0]
            cod_produt = cachedUpdate[1]
            cod_lote = cachedUpdate[3]
            qtd_produt = cachedUpdate[4]
            dat_vctlot = str(telaUpdate.dateEditVenc.text())
            cod_lote_new= telaUpdate.lineEditLote.text()

            
            update_produt(cod_loja,cod_bal,cod_produt,cod_lote,qtd_produt,dat_vctlot,cod_lote_new)
           


        else:
            print('Erro on_update')
            return
        

    except Exception as e:
        s = 'Erro on_update'
        logging.warning(date_time()+s)
        logging.warning(e)
        
def sair_produt():
    telaProdutIns.close()

def sair_remove_produt():
    telaRemov.close()

def sair_update_produt():
    telaUpdate.close()

#Funções das telas
def tela_add_produt():
    try:
        telaProdutIns.show()
        telaProdutIns.lineEditCodProdut.setFocus()
    except Exception as e:
        s = 'Erro tela_add_produt'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)          

def refreshList(cod_bal):
    try:
        # Setando numero de linhas, colunas e nome das colunas
        telaPrincipal.tableWidget.setRowCount(len(list_produt(cod_bal)))
        telaPrincipal.tableWidget.setColumnCount(len(list_produt(cod_bal)[0]))
        # Inserindo os dados na tabela
        rows = list_produt(cod_bal)

        for i in range(len(rows)): #linha
            for j in range(len(rows[0])): #coluna
                item = QtWidgets.QTableWidgetItem(f"{rows[i][j]}")
                telaPrincipal.tableWidget.setItem(i,j, item)
    except Exception as e:
        s = 'Erro refresh_list'
        logging.warning(date_time()+s)
        logging.warning(date_time()+e)
        
def tela_notif(text_on,text_two):
    
    telaNotif.show()
    telaNotif.label.setText(text_on)
    telaNotif.label_2.setText(text_two)
    telaNotif.btnOk.setFocus()

    return
    
def tela_produt_close():
    telaProdutIns.close()

def tela_notif_close():
    telaNotif.close()

def on_selectionChanged( selected, deselected):
    if  selected != []:
        
        #self.tb_company.selectionModel().currentIndex().siblingAtColumn(0).data()
        codigo=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
        lote=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(2).data()
        print(codigo)
        print(lote)
        for ix in selected.indexes():
            print('Selected Cell Location Row: {0}, Column: {1}'.format(ix.row(), ix.column()))

        for ix in deselected.indexes():
            print('Deselected Cell Location Row: {0}, Column: {1}'.format(ix.row(), ix.column()))
				
def on_selected(selected):
    if  selected != []:
        cod_produt=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
        cod_lote=telaPrincipal.tableWidget.selectionModel().currentIndex().siblingAtColumn(2).data()
        print(cod_produt)
        print(cod_lote)
        telaPrincipal.btnEdit.setEnabled(True)
        telaPrincipal.btnRemove.setEnabled(True)





#Atribui funcoes a interface grafica
telaLogin.btnEntrar.clicked.connect(valida_login)
telaLogin.btnEntrar.clicked.connect(valida_login)

telaPrincipal.btnAdd.clicked.connect(tela_add_produt)
telaPrincipal.btnEdit.clicked.connect(editProdut)
telaPrincipal.btnRemove.clicked.connect(removeProdut)
telaPrincipal.tableWidget.selectionModel().selectionChanged.connect(on_selected)
telaPrincipal.lineEditCodBal.returnPressed.connect(valida_cod_bal)

telaProdutIns.btnAplic.clicked.connect(valida_produt)
telaProdutIns.btnSair.clicked.connect(valida_produt)
telaProdutIns.lineEditCodProdut.returnPressed.connect(valida_codprodut)
telaProdutIns.btnSair.clicked.connect(sair_produt)

telaNotif.btnClose.clicked.connect(tela_notif_close)
telaNotif.btnOk.clicked.connect(tela_notif_close)


telaRemov.btnYes.clicked.connect(on_remove)
telaRemov.btnNo.clicked.connect(sair_remove_produt)
telaRemov.btnClose.clicked.connect(sair_remove_produt)

telaUpdate.btnAtualiz.clicked.connect(on_update)
#telaProdutIns.setWindowFlags(telaProdutIns.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

telaLogin.show()
app.exec()
