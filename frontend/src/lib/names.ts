const FIRST_NAMES: readonly string[] = [
  "Ana",
  "Bruno",
  "Carla",
  "Diego",
  "Elisa",
  "Felipe",
  "Gabriela",
  "Henrique",
  "Isabela",
  "João",
  "Karina",
  "Lucas",
  "Marina",
  "Nicolas",
  "Olivia",
  "Pedro",
  "Quésia",
  "Rafael",
  "Sofia",
  "Thiago",
  "Úrsula",
  "Vitor",
  "Wanda",
  "Xavier",
  "Yasmin",
  "Zeca",
  "Alice",
  "Bernardo",
  "Camila",
  "Daniel",
  "Eduarda",
  "Fábio",
  "Giovana",
  "Hugo",
  "Ingrid",
  "Julio",
  "Larissa",
  "Mateus",
  "Natália",
  "Otávio",
];

const LAST_NAMES: readonly string[] = [
  "Almeida",
  "Barbosa",
  "Carvalho",
  "Dias",
  "Esteves",
  "Ferreira",
  "Gomes",
  "Henriques",
  "Lima",
  "Martins",
  "Nogueira",
  "Oliveira",
  "Pereira",
  "Ramos",
  "Silva",
  "Teixeira",
  "Ugarte",
  "Vieira",
  "Xavier",
  "Moreira",
  "Costa",
  "Rocha",
];

const pick = <T>(items: readonly T[], random: () => number): T =>
  items[Math.floor(random() * items.length)];

// Gera `count` nomes completos aleatórios e distintos entre si.
export function randomNames(
  count: number,
  random: () => number = Math.random,
): string[] {
  const names = new Set<string>();
  const maxUnique = FIRST_NAMES.length * LAST_NAMES.length;
  while (names.size < Math.min(count, maxUnique)) {
    names.add(`${pick(FIRST_NAMES, random)} ${pick(LAST_NAMES, random)}`);
  }
  return [...names];
}
