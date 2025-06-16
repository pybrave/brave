include {strainphlan} from './modules/strainphlan.nf'
include {tree_pairwisedists} from './modules/strainphlan.nf'

workflow  {
    ch_pkl= Channel.value("/data/wangyang/databases/metaphlan/mpa_vJun23_CHOCOPhlAnSGB_202403.pkl")
    ch_reference = Channel.value(params.reference)
    // ch_input = channel.fromList(params.samples).map(it->it.json).collect()
    ch_input = channel.value(params.samples)
    ch_clade =  channel.fromList(params.clade )
    // ch_clade.view()
    // ch_input.view()
    ch_strainphlan_out = strainphlan(ch_input,false,ch_pkl,ch_clade)
    // ch_strainphlan_out.bestTree.view()
    tree_pairwisedists(ch_strainphlan_out.bestTree)
    // sample2markers(ch_input,ch_pkl)
    

}