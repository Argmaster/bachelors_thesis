# Cel pracy

Celem mojej pracy jest re-implementacja programu do detekcji splątania kwantowego z
modyfikacjami które pozwolą na zminimalizowanie czasu koniecznego do analizy obszernych
zbiorów macierzy gęstości, następnie analiza skuteczności różnych metod które
potencjalnie mogły oferować zwiększenie przepustowości obliczeniowej kodu oraz
podsumowanie uzyskanych wyników wraz z rekomendacjami dotyczącymi zastosowania wybranych
implementacji do rozwiązywania problemów naukowych.

Zwieńczeniem moich prac są cztery funkcjonalne alternatywne implementacji algorytmu, z
których najwydajniejsza oferuje kilkukrotną znaczącą poprawę wydajności względem
oryginalnego kodu. Zarówno dla tych implementacji które upubliczniłem jak i dla
zmodyfikowanych ich wariantów uzyskałem pomiary czasu pracy dla 6 różnych macierzy
gęstości. Wyniki będę sukcesywnie prezentował w dalszej części pracy.

# Metody

Profilowanie kodu

Python - cProfile

Rust - perf
