import pandas as pd
import plotly.express as px

def virus_pie_charts_report(temp, virus_report):

    table = pd.read_csv(virus_report, sep='\t')
    nt_viruses = table[table['nt_sskingdom'] == 'Viruses']['nt_ssciname']
    nr_viruses = table[table['nr_sskingdom'] == 'Viruses']['nr_ssciname']

    count_nt = nt_viruses.value_counts()
    count_nr = nr_viruses.value_counts()
    pie_table_nt = pd.DataFrame({'name' : count_nt.index.to_list(), 'count':count_nt.to_list() })
    pie_table_nr = pd.DataFrame({'name' : count_nr.index.to_list(), 'count':count_nr.to_list() })

    fig_nt = px.pie(pie_table_nt, values='count', names='name', title='Viruses from nucletide search')
    fig_nt.update_traces(textposition='inside', textinfo='label')

    fig_nr = px.pie(pie_table_nr, values='count', names='name', title='Viruses from protein search')
    fig_nr.update_traces(textposition='inside', textinfo='label')

    html = temp.compose_filename("viruses_report.html")

    with open(html, 'a') as f:
        f.write(fig_nt.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig_nr.to_html(full_html=False, include_plotlyjs='cdn'))