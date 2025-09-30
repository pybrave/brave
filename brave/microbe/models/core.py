
from datetime import datetime
from sqlalchemy import Column, DateTime, Table
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from brave.api.config.db import meta
# from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Text,Index,UniqueConstraint
from sqlalchemy.dialects.mysql import LONGTEXT



t_taxonomy = Table(
    "taxonomy",
    meta,
    # --- nodes.dmp 字段 ---
    Column("tax_id", Integer, primary_key=True, autoincrement=False),   

    Column("entity_id", String(255),  nullable=False, index=True),   

    # tax_id: 物种节点ID (唯一编号)，作为主键

    Column("parent_tax_id", Integer, nullable=False, index=True),       
    # parent_tax_id: 父节点ID，用于构建层级关系 (species → genus → family ...)

    Column("rank", String(50), nullable=False, index=True),             
    # rank: 分类等级 (domain, kingdom, phylum, class, order, family, genus, species)

    # Column("embl_code", String(20)),                                    
    # embl_code: EMBL 数据库 locus 前缀（非唯一，可为空）

    Column("division_id", Integer),                              
    # division_id: division.dmp 中定义的 division ID（生物学分区，例如 Bacteria, Vertebrates）
    
    Column("division_name",  String(255)), 
    # Column("division_code", Integer),     
    # Column("inherited_div_flag", SmallInteger),                         
    # inherited_div_flag: 是否继承 division (1 = 是，0 = 否)

    # Column("genetic_code_id", Integer),                                 
    # genetic_code_id: gencode.dmp 中定义的遗传密码表 ID

    # Column("inherited_gc_flag", SmallInteger),                          
    # inherited_gc_flag: 是否继承遗传密码表 (1 = 是，0 = 否)

    # Column("mitochondrial_genetic_code_id", Integer),                   
    # mitochondrial_genetic_code_id: gencode.dmp 中的线粒体遗传密码表 ID

    # Column("inherited_mgc_flag", SmallInteger),                         
    # inherited_mgc_flag: 是否继承线粒体遗传密码表 (1 = 是，0 = 否)

    # Column("genbank_hidden_flag", SmallInteger),                        
    # genbank_hidden_flag: 是否在 GenBank lineage 中隐藏该节点 (1 = 隐藏)

    # Column("hidden_subtree_root_flag", SmallInteger),                   
    # hidden_subtree_root_flag: 是否为“未有序列数据的子树根” (1 = 是)

    # Column("comments", Text),                                           
    # comments: 自由文本注释（引用、备注）

    # --- names.dmp (只保留 scientific name) ---
    Column("entity_name", String(255), nullable=False, index=True),
    # scientific_name: 学名（唯一科学名称，过滤 name_class='scientific name'）

    # 额外索引：提高 scientific_name 的查询效率
    # Index("idx_name", "scientific_name"),
)

# t_entity = Table(
#     "entity",
#     meta,
#     Column("id", Integer, primary_key=True),
#     Column("entity_id", String(255)),
#     Column("entity_name", String(255)),
#     Column("reference_id", String(255)),
#     Column("is_research", Boolean, default=False),
#     Column("created_at", DateTime, default=datetime.now),
#     Column("updated_at", DateTime, onupdate=datetime.now)
# )


t_study = Table(
    "study",
    meta,
    # 主键：每个研究唯一

    Column("entity_id", String(50), primary_key=True, index=True),
    Column("parent_entity_id", String(50),  index=True),       

    Column("entity_name", String(200) , nullable=False, index=True),
    Column("title", Text, comment="研究标题"),
    Column("overall_design", Text, comment="研究总体设计"),
    Column("criteria_for_disorder", Text, comment="疾病诊断或入选标准"),
    Column("fulltext",Text().with_variant(LONGTEXT(), "mysql")),

    Column("sample_size", Integer, comment="单组样本量"),
    Column("total_sample_size", Integer, comment="总样本量"),
    Column("age", String(50), comment="平均年龄或年龄范围"),
    Column("sex", String(50), comment="性别比例，如 male/female"),
    Column("bmi", String(50), comment="BMI，若有"),
    Column("amplicon_region", String(50), comment="16S rRNA测序区域"),
    
    Column("processing_software", String(255), comment="数据处理软件"),
    Column("reference_database", String(255), comment="参考数据库"),
    Column("original_data_available", String(255), comment="原始数据是否可用"),
    
    Column("pmcid", String(255), comment="PubMed ID"),
    Column("pmid", String(255), comment="PubMed ID"),
    Column("doi", String(255), comment="DOI"),
    Column("country", String(255), comment="研究国家/地区"),
    
    Column("citation", Text, comment="完整引用信息"),
    Column("pubmed_link", String(255), comment="PubMed链接"),
    Column("doi_link", String(255), comment="DOI链接"),
)


t_disease = Table(
    "disease",
    meta,
    Column("entity_id", String(50), primary_key=True, index=True),
    Column("entity_name", String(255) , nullable=False, index=True),
    Column("mesh_id", String(255) , nullable=False, index=True),
    Column("parent_entity_id", String(255),  index=True)

)    

# CREATE INDEX idx_taxonomy_entity_id ON taxonomy(entity_id);
# CREATE INDEX idx_mesh_second_entity_id ON mesh(second_entity_id);

# SELECT * from mesh 
# LEFT JOIN mesh_tree on mesh.entity_id = mesh_tree.entity_id
# where category='B01'

# SELECT * from mesh 
# LEFT JOIN mesh_tree on mesh.entity_id = mesh_tree.entity_id
# LEFT  JOIN taxonomy on mesh.second_entity_id =taxonomy.entity_id 
# where category='B01'

t_mesh = Table(
    "mesh",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True), 
    Column("entity_id", String(50),nullable=False),
    Column("entity_name", String(255) , nullable=False, index=True),
    # Column("second_entity_id", String(50), index=True),
    Column("is_research", Boolean, default=False),
    Column("entity_type", String(255)),
    Column("tags",Text().with_variant(LONGTEXT(), "mysql")),
    Column("short_name",Text().with_variant(LONGTEXT(), "mysql")),
    Column("describe",Text().with_variant(LONGTEXT(), "mysql")),

    Column("entity_name_zh", String(255) , index=True),
    UniqueConstraint("entity_id", name="uniq_entity_id")
    
) 
t_registry_numbers = Table(
    "registry_numbers",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("entity_id", String(50), nullable=False, index=True),  # 外键关联到 t_mesh.entity_id
    Column("registry_number", String(50), nullable=False, index=True),
    Column("registry_type", String(50), nullable=False, server_default="_NULL_", index=True),  # CAS / EC / TXID / Other
    UniqueConstraint("entity_id", "registry_number", name="uniq_registry_number")
)
t_mesh_tree  = Table(
    "mesh_tree",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True), 
    Column("entity_id", String(50) , nullable=False, index=True),
    Column("tree_number", String(255),  index=True),
    Column("category", String(50),  index=True),
    Column("parent_tree", String(255), nullable=False, server_default="_NULL_", index=True),
    UniqueConstraint("entity_id", "tree_number", "parent_tree", name="uniq_mesh_tree")
) 

# Column("major_category", String(50),  index=True),

# t_intevention = Table(
#     "intevention",
#     meta,
#     Column("entity_id", String(50), primary_key=True, index=True),
#     Column("entity_name", String(255) , nullable=False, index=True),
#     Column("parent_entity_id", String(255),  index=True)
# )    

t_chemicals_and_drugs  = Table(
    "chemicals_and_drugs",
    meta,
    Column("entity_id", String(50), primary_key=True, index=True),
    Column("entity_name", String(255) , nullable=False, index=True),
    Column("parent_entity_id", String(255),  index=True)
)   

t_diet_and_food  = Table(
    "diet_and_food",
    meta,
    Column("entity_id", String(50), primary_key=True, index=True),
    Column("entity_name", String(255) , nullable=False, index=True),
    Column("parent_entity_id", String(255),  index=True)
)  

t_association  = Table(
    "association",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True), 
    Column("entity_id", String(255),  index=True),
    Column("subject_id", String(255)), # Subject = 作用者（who does something）
    Column("object_id", String(255)), # Object = 被作用者（who receives the effect）
    Column("observed_id", String(255)), 
    Column("study_id", String(255)),
    Column("predicate", String(255)),
    Column("effect", String(255)),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
    # Column("participates_in_pathway", String(255)),
    # Column("produces_metabolite", String(255)),
    # Column("regulates_gene", String(255)),
)