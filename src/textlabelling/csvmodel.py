class CSVModel:
    def __init__(self,  output_dir:str):
        self.output_dir=output_dir
        


    def load_model(self):
        print("Loading from", self.output_dir)
        nlp = spacy.load(self.output_dir)
        return nlp


    def write_result_csv(self, DATA:list, filename:str)->str:
        nlp = self.load_model()
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['text','intents','classes'])
            for text in DATA:
                intents = []
                labels = []
                doc = nlp(text)
                for ent in doc.ents:
                    intents.append(ent.text)
                    labels.append(ent.label_)
                    writer.writerow([text,intents,labels])
        print(f'{filename} has been created')
            #print([(text, ent.text, ent.label_)for ent in doc.ents])
            #print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    def write_df_csv(self, df:pd.DataFrame, filename:str)->str:
        nlp = self.load_model()
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['created_date','nps_vervatism','nps_score','intents','classes'])
            for index, row in df.iterrows():
                intents = []
                labels = []
                if type(row[1])==str:
                    if len(row[1])>1:
                        doc = nlp(row[1])
                        for ent in doc.ents:
                            intents.append(ent.text)
                            labels.append(ent.label_)
                            writer.writerow([row[0],row[1],row[2],intents,labels])

       
    def print_result_console(self, df:pd.DataFrame)->str:
        nlp = self.load_model()
        for index, row in df.iterrows():
            intents = []
            labels = []
            if type(row[2])==str:
                if len(row[2])>1:
                    doc = nlp(row[2])
                    for ent in doc.ents:
                        intents.append(ent.text)
                        labels.append(ent.label_)
                        print(f'NPS_Score: {row[2]}')
                        print(f'NPS_verbatism:{row[1]}')
                        print('intent:', intents)
                        print('entities:', labels)
                        print('')
