import unittest

from xcomagents import genetics


class TestAlgoritmosGeneticos(unittest.TestCase):
    def generate_mock_pop(self):
        poblacion = [genetics.Chromosome([1,2,3,4,5]),genetics.Chromosome([3,4,5,6,7]),genetics.Chromosome([6,7,8,9,10]), genetics.Chromosome([7,8,9,10,11])]
        fitness = [1,4,6, 3]
        for i in range(len(poblacion)):
            poblacion[i].fitness = fitness[i]
        return poblacion
    
    def test_generate(self):
        cantidad = 20
        cromosome = genetics.generate(cantidad)
        self.assertEqual(type(cromosome), list)
        self.assertTrue(all(g in range(10) for g in cromosome))
        self.assertEqual(len(cromosome), cantidad)
    
    def test_generate_pop_wrong_agents(self):
        agentes = -1
        roles = 2
        population = 10
        result = genetics.generate_pop(population, agentes, roles)
        self.assertEqual(result, -1)
    
    def test_generate_pop_wrong_roles(self):
        agentes = 10
        roles = 0
        population = 10
        result = genetics.generate_pop(population, agentes, roles)
        self.assertEqual(result, -1)
    
    def test_generate_pop_wrong_population(self):
        agentes = 10
        roles = 3
        population = 0
        result = genetics.generate_pop(population, agentes, roles)
        self.assertEqual(result, -1)
    
    def test_generate_pop_valid(self):
        agentes = 8
        roles = 5
        population = 10
        result = genetics.generate_pop(population, agentes, roles)
        self.assertTrue(all(type(c) == genetics.Chromosome for c in result))
        self.assertEqual(len(result), population)
        cromosomas = [tuple(c.values) for c in result]
        self.assertEqual(len(cromosomas), len(set(cromosomas)))
        self.assertTrue(all(len(c.values) == agentes * roles for c in result))
    
    def test_cross(self):
        madre = genetics.Chromosome([4,4,4,4,4])
        padre = genetics.Chromosome([5,5,5,5,5])
        hijo1, hijo2 = genetics.cross(madre,padre)
        self.assertEqual(len(hijo1.values), len(madre.values))
        self.assertEqual(len(hijo2.values), len(madre.values))
        self.assertNotEqual(madre.values, hijo1.values)
        self.assertNotEqual(madre.values, hijo2.values)
        self.assertNotEqual(padre.values, hijo2.values)
        self.assertNotEqual(padre.values, hijo1.values)
    
    def test_tournament_choice(self):
        poblacion = self.generate_mock_pop()
        chosen = genetics.tournmanet_choice(poblacion,k=4)
        self.assertEqual(chosen, poblacion[2])
    
    def test_tournament_choice_bad_k_less(self):
        poblacion = self.generate_mock_pop()
        with self.assertRaises(ValueError):
            chosen = genetics.tournmanet_choice(poblacion,k=-1)
    
    
    def test_tournament_choice_bad_not_enough_pop(self):
        poblacion = self.generate_mock_pop()
        with self.assertRaises(ValueError):
            chosen = genetics.tournmanet_choice(poblacion,k=5)

    def test_tournament_choice_bad_population(self):
        poblacion = []
        with self.assertRaises(IndexError):
            chosen = genetics.tournmanet_choice(poblacion,k=0)

    def test_new_generation_roulette(self):
        poblacion = self.generate_mock_pop()
        crossover = 1
        new_pop = genetics.new_generation_roulette(poblacion,crossover)
        self.assertEqual(len(new_pop), len(poblacion))
        self.assertTrue(new_pop[0] in poblacion)

    def test_new_generation_roulette_bad_population(self):
        poblacion = []
        crossover = 1
        with self.assertRaises(IndexError):
            new_pop = genetics.new_generation_roulette(poblacion,crossover)

    def test_new_generation_tournament(self):
        poblacion = self.generate_mock_pop()
        crossover = 1
        k = 3
        new_pop = genetics.new_generation_tournament(poblacion,k,crossover)
        self.assertEqual(len(new_pop), len(poblacion))
        self.assertTrue(new_pop[0] in poblacion)

    def test_new_generation_tournament_bad_k(self):
        poblacion = self.generate_mock_pop()
        crossover = 1
        k = -1
        with self.assertRaises(ValueError):
            new_pop = genetics.new_generation_tournament(poblacion,k,crossover)


    def test_new_generation_tournament_bad_population(self):
        poblacion = []
        crossover = 1
        k = 3
        with self.assertRaises(IndexError):
            new_pop = genetics.new_generation_tournament(poblacion,k,crossover)


if __name__== "__main__":
    unittest.main()
