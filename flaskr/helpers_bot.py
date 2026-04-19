from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout


def _calcular_interno(comando: str) -> str:
    """Roda em processo separado — seguro matar no timeout."""
    import sympy as sp
    import sympy.physics.units as u
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations, implicit_multiplication_application
    )
    def _log10(x): return sp.log(x, 10)
    def _log2(x):  return sp.log(x, 2)


    transformations = standard_transformations + (implicit_multiplication_application,)
    contexto_matematico = {
            # === Constantes físicas fundamentais ===
            'G'     : u.gravitational_constant,   # constante gravitacional
            'c'     : u.speed_of_light,           # velocidade da luz
            'h'     : u.planck,                  # constante de Planck
            'hbar'  : u.hbar,                    # constante de Planck reduzida
            'kb'    : u.boltzmann_constant,      # constante de Boltzmann
            'NA'    : u.avogadro_number,         # número de Avogadro
            'e'     : u.elementary_charge,       # carga elementar
            'me'    : u.electron_rest_mass,      # massa do elétron
            'mp'    : sp.Float(1.67262192e-27),  # massa do próton (kg)
            'mn'    : sp.Float(1.67492749e-27),  # massa do nêutron (kg)
            'eps0'  : u.vacuum_permittivity,     # permissividade do vácuo
            'mu0'   : u.magnetic_constant,       # permeabilidade do vácuo (μ₀)
            'R'     : u.molar_gas_constant,      # constante dos gases ideais
            'sigma' : u.stefan_boltzmann_constant, # constante de Stefan-Boltzmann
            'F'     : u.faraday_constant,        # constante de Faraday
            'atm'   : u.atm,                     # pressão atmosférica

            # === Constantes matemáticas ===
            'pi'    : sp.pi,     # π
            'E'     : sp.E,      # número de Euler
            'oo'    : sp.oo,     # infinito
            'I'     : sp.I,      # unidade imaginária
            
            # === Variáveis simbólicas padrão ===
            'x': sp.Symbol('x'),
            'y': sp.Symbol('y'),
            'z': sp.Symbol('z'),
            't': sp.Symbol('t'),
            'n': sp.Symbol('n'),
            'k': sp.Symbol('k'),
            'a': sp.Symbol('a'),
            'b': sp.Symbol('b'),
            'm': sp.Symbol('m'),
            'v': sp.Symbol('v'),
            'r': sp.Symbol('r'),
            
            # === Operações algébricas ===
            'factor'    : sp.factor,     # fatoração
            'expand'    : sp.expand,     # expansão
            'simplify'  : sp.simplify,   # simplificação
            'diff'      : sp.diff,       # derivada
            'integrate' : sp.integrate,  # integral
            'solve'     : sp.solve,      # resolver equações
            'limit'     : sp.limit,      # limite
            'series'    : sp.series,     # série de Taylor
            'Sum'       : sp.Sum,        # somatório
            'Product'   : sp.Product,    # produtório
            'Matrix'    : sp.Matrix,     # matrizes
            'Rational'  : sp.Rational,   # números racionais
            'Abs'       : sp.Abs,        # valor absoluto
            're'        : sp.re,         # parte real
            'im'        : sp.im,         # parte imaginária
            'conjugate' : sp.conjugate,  # conjugado complexo
            
            # === Funções trigonométricas ===
            'sin'   : sp.sin,
            'cos'   : sp.cos,
            'tan'   : sp.tan,
            'asin'  : sp.asin,
            'acos'  : sp.acos,
            'atan'  : sp.atan,
            'atan2' : sp.atan2,
            'sinh'  : sp.sinh,
            'cosh'  : sp.cosh,
            'tanh'  : sp.tanh,
            
            # === Funções gerais ===
            'sqrt'  : sp.sqrt,            # raiz quadrada
            'exp'   : sp.exp,             # exponencial
            'log'   : sp.log,             # log natural
            'log10' : _log10,  # log base 10
            'log2'  : _log2,   # log base 2
            'floor' : sp.floor,
            'ceiling': sp.ceiling,
            'sign'  : sp.sign,
            'factorial': sp.factorial,
            'binomial' : sp.binomial,
            'gcd'      : sp.gcd,
            'lcm'      : sp.lcm,
            
            # === Funções especiais ===
            'gamma' : sp.gamma,
            'beta'  : sp.beta,
            'erf'   : sp.erf,
            'erfc'  : sp.erfc,
            'DiracDelta' : sp.DiracDelta,
            'Heaviside'  : sp.Heaviside,
            'besselj'    : sp.besselj,
            'bessely'    : sp.bessely,

            # === Estruturas matemáticas ===
            'S'     : sp.S,
            'FiniteSet'  : sp.FiniteSet,
            'Interval'   : sp.Interval,
            
            
            'N' : sp.N, 
        }

    result = parse_expr(comando, local_dict=contexto_matematico, transformations=transformations)
    return str(sp.simplify(result))


def executar_calculos(comando: str) -> str:
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_calcular_interno, comando)
        try:
            return future.result(timeout=10)
        except FuturesTimeout:
            future.cancel()
            return "Erro: expressão muito complexa (timeout de 10s)"
        except Exception as e:
            return f"Erro: {e}"
        
if __name__ == '__main__':
    pass       