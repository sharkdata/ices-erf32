from erf32_generator.erf32_filters import Erf32Filters
from erf32_generator.erf32_translate import Erf32Translate
# from erf32_generator.erf32_taxa_worms import Erf32SpeciesWorms
from erf32_generator.erf32_data_shark import Erf32DataShark

from erf32_generator.export_ices_utils import ExportStations
from erf32_generator.export_ices_utils import TranslateTaxa
from erf32_generator.export_ices_utils import TranslateDyntaxaToHelcomPeg

from erf32_generator.export_ices_generator import GenerateIcesErf32
from erf32_generator.export_ices_format import IcesErf32Format
from erf32_generator.export_ices_content import ExportIcesContent
from erf32_generator.export_ices_transects import TransectData
from erf32_generator.generator_config import GeneratorConfig

# Instead of using the singleton pattern.
global_filters = Erf32Filters()
global_translate = Erf32Translate()
global_export_stations = ExportStations()
global_translate_taxa = TranslateTaxa()
global_translate_dyntaxa_to_helcom_peg = TranslateDyntaxaToHelcomPeg()
global_transect_data = TransectData()

