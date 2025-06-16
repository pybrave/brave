include {metaphlan_sam} from './modules/metaphlan.nf'

workflow  {
   ch_metaphlan_db = Channel.value("/data/wangyang/databases/metaphlan")

   ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key,nreads:it.nreads],it.bam])
//    ch_input.view()
   metaphlan_sam(ch_input, ch_metaphlan_db)
}