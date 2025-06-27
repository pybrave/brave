
+ RPKs=Reads Per Kilobase(每千碱基读取数)
    + RPK = Reads mapped to a feature / Feature length in kilobases
    + RPK = 100 reads / 2 kb = 50 RPK
+ [ref](https://github.com/biobakery/biobakery/wiki/humann3#3-manipulating-humann-output-tables)

不同样本的总 reads 数不同，不能直接比较。RPK 是按长度归一化了，但还没考虑样本测序深度。

为了便于比较不同测序深度的样本，在进行统计分析之前，必须对 HUMAnN 的默认 RPK 值进行归一化处理。将总和归一化为相对丰度或 "百万拷贝数"（CPM）单位是常用的方法；这些方法在 humann_renorm_table 脚本中实现（对 HUMAnN 的输出格式有特殊考虑，如特征分层）
```
humann_renorm_table --input demo_fastq/demo_genefamilies.tsv \
    --output demo_fastq/demo_genefamilies-cpm.tsv --units cpm --update-snames
```