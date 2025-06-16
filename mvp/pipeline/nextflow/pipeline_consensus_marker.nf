include {sample2markers} from './modules/strainphlan.nf'
workflow  {
    ch_pkl= Channel.value("/data/wangyang/databases/metaphlan/mpa_vJun23_CHOCOPhlAnSGB_202403.pkl")
    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key,nreads:it.nreads],it.bam])
    sample2markers(ch_input,ch_pkl)
    

}