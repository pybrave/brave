include {humann} from './modules/humann.nf'
workflow  {

   ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2],it.profile])
//    ch_input.view()
   humann(ch_input)
}