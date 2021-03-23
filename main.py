import streamlit as st
import pandas as pd
from PIL import Image
#from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
#from weasyprint import HTML
import pdfkit

#templates em html
head_message_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6> 
<h6>Post Date: {}</h6> 
</div>
"""
full_message_temp ="""
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""



#configurando página
logo_image = Image.open("logo.jfif")
PAGE_CONFIG = {'page_title':'Riverdata Relatório' , 'page_icon':logo_image}
st.set_page_config(**PAGE_CONFIG)

#Função para download do banco de dados como pdf

def create_download_link(path, filename):
    with open(path, 'rb') as f:
        val = f.read()
        b64 = base64.b64encode(val)  # val looks like b'...'
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.html">Fazer Download do Arquivo</a>'




# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
# DB Management
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data



def main():
    """Simple Login App"""

    st.sidebar.image(logo_image, width=150)
    st.title("Relatório Rivertemp")

    menu = ["Home","Login"]
    choice = st.sidebar.selectbox("Menu",menu)


    if choice == "Home":
        imagem = Image.open("Rivertemp.jpg")
        st.subheader("Home")
        st.markdown("Aplicativo Web, desenvolvido a fim de automatizar o processo de análise dos dados provenientes do Rivertemp")
        st.markdown("Na página de Login e Análise, arraste e solte(ou pesquise no gerenciador de arquivos) um arquivo de dados do tipo .csv")
        st.markdown("Desta forma o aplicativo irá gerar um relatório automático do banco de dados, assim como disponibilizar o download da tabela")
        st.markdown("Para saber mais acesse o site da [Riverdata](https://riverdata.com.br/)")
        st.image(imagem)


    elif choice == "Login":
        st.subheader("Seção de Login")

        username = st.sidebar.text_input("Nome de Usuário")
        password = st.sidebar.text_input("Senha",type='password')
        if st.sidebar.checkbox("Login"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:

                st.success("Conectado como {}".format(username))

                task = st.selectbox("Tarefa",["Adicionar Post","Análise","Profiles", "Inscrever novo Usuário"])
                if task == "Adicionar Post":
                    st.subheader("Addicione Seu Post")
                    b_author = st.text_input("Enter Author Name",max_chars=50)
                    b_title = st.text_input("Enter Post Title")
                    b_article = st.text_area("Post Article Here",height=200)
                    b_post_date = st.date_input("Date")
                    if st.button("Add"):
                        st.markdown(head_message_temp.format(b_title,b_author,b_post_date),unsafe_allow_html=True)
                        st.markdown(full_message_temp.format(b_article),unsafe_allow_html=True)

                elif task == "Análise":
                    st.subheader("Análise")
                    st.subheader("Carregar arquivo de banco de dados para obter o relatório")
                    dataset = st.file_uploader("Faça o Upload do arquivo csv a ser analisado:", type=['csv'])
                    if dataset:
                        #imprimir tabela
                        df = pd.read_csv(dataset, names=['Temperatura','Data_Hora', '0'])
                        df = df.drop(columns=['0'])
                        df.Data_Hora = pd.to_datetime(df.Data_Hora, unit='ms')
                        df.Data_Hora = df.Data_Hora.dt.strftime("%d/%m/%Y %H:%M")
                        df.Temperatura = df.Temperatura.astype(float)
                        st.dataframe(df)


                        #Download Table
                        df.to_html('Banco de dados Tabela.html')
                        #tabela = pdfkit.from_file('Banco de dados Tabela.html', 'Banco de dados Tabela.pdf')
                        #tabela = weasyprint.HTML('/content/Rivertemp_Aerki_Burguer_Tabela.html').write_pdf()
                        #open('Rivertemp_Aerki_Burguer_Tabela.pdf', 'wb').write(tabela)
                        export_as_pdf = st.button("Exportar Banco de Dados em Tabela")
                        if export_as_pdf:

                            html = create_download_link('Banco de dados Tabela.html', "Rivertemp_Aerki_Burguer_Tabela")
                            st.markdown(html, unsafe_allow_html=True)



                        #Plotar Gráfico
                        df.set_index('Data_Hora', inplace = True)
                        #df = df.drop(columns=['Data_Hora'])
                        fig, ax = plt.subplots()
                        ax.plot(df.index, df.Temperatura)
                        ax.set_title('Evolução Diaria da Temperatura Média por Hora Aerki Burguer\n')
                        #ax.tick_params(axis='x', labelrotation=45)
                        ax.set_xlabel("Data")
                        ax.set_ylabel("Temperatura")
                        plt.xticks(df.index.values[::1000], rotation=45)
                        #legend = ax.legend(loc='upper right')
                        st.pyplot(fig)

                elif task == "Profiles":
                    st.subheader("Profiles dos Usuários")
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result,columns=["Nome de Usuário","Senha"])
                    st.dataframe(clean_db)

                elif task == "Inscrever novo Usuário":
                    st.subheader("Criar novo Usuário")
                    new_user = st.text_input("nome do novo usuário")
                    new_password = st.text_input("senha",type='password')

                    if st.button("Inscrever novo Usuário"):
                        create_usertable()
                        add_userdata(new_user,make_hashes(new_password))
                        st.success("Você criou uma nova conta com sucesso!")
                        st.info("Vá para o portal de Login")

                    else:
                        st.warning("Nome de Usuário ou Senha incorretos")


if __name__ == '__main__':
    main()
