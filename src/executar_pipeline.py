import ingerir_transfers
import ingerir_brasileirao
import explorar
import transformar_transfers
import transformar_brasileirao

def main():
    print("--- 1. Iniciando ingestão da Camada Bronze: Transfermarkt ---")
    ingerir_transfers.main()
    
    print("\n--- 2. Iniciando ingestão da Camada Bronze: Brasileirão ---")
    ingerir_brasileirao.main()
    
    print("\n--- 3. Iniciando exploração automatizada (Profiling) ---")
    explorar.main()
    
    print("\n--- 4. Iniciando transformação da Camada Prata: Transfermarkt ---")
    transformar_transfers.main()
    
    print("\n--- 5. Iniciando transformação da Camada Prata: Brasileirão ---")
    transformar_brasileirao.main()
    
    print("\n--- Pipeline das Camadas Bronze e Prata concluído com sucesso! ---")

if __name__ == "__main__":
    main()