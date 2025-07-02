import { Button, Form, Input, InputNumber, Select } from "antd";
import TextArea from "antd/es/input/TextArea";
import axios from "axios";
import { Component, FC, useEffect, useState, memo } from "react";
import { data } from "react-router";
const FormJsonComp: FC<any> = memo(({ formJson, dataMap }) => {
    const componentMap: any = {
        GroupSelect: {
            Component: BaseSelect,
            dataKey: "sample_group_list"
        },
        GroupCompareSelect: {
            Component: GroupCompareSelect,
        },
        BaseSelect: {
            Component: BaseSelect,
        },
        BaseInputNumber: {
            Component: BaseInputNumber,
        },
        BaseInput: {
            Component: BaseInput,
        },
        RankSelect: {
            Component: BaseSelect,
            dataKey: "rank",
            mode: undefined,
            initialValue: "SPECIES"
        }, GroupFieldSelect: {
            Component: BaseSelect,
            dataKey: "group_field",
            mode: undefined,
            initialValue: "sample_group"
        }, FilterFieldSelect: {
            Component: FilterSelect,
            dataKey: "sample_group_list",
            mode: undefined,
            // initialValue:"sample_group"
        },
        GroupSelectSampleButton: {
            Component: GroupSelectSampleButton,
            dataKey: "sample_group_list"
        }, MetaphlanCladeSelect: {
            Component: MetaphlanCladeSelect,
        }, SelectAll: {
            Component: SelectAll,
            dataKey: "sample_group_list"
        }
    };
    const ComponentsRender = ({ type, dataMap, inputAnalysisMethod, dataKey: dataKey_, data: data_, name, inputKey, ...rest }: any) => {
        if(!dataMap) return  (() => <div>加载中....</div>)
        const componentObj = componentMap[type] //|| (() => <div>未知类型</div>);
        // if (first_data_key in dataMap_)
        // if(!dataMap_ && !dataMap_.first_data_key){
        //     dataMap_.first_data_key  =""
        // }
        // const { first_data_key, ...dataMap } = dataMap_
        if (!componentObj) {
            return <div>未知类型 {type}</div>
        }
        // debugger
        const { Component, ...crest } = componentObj
        // debugger


        let data: any = []
        if (data_) {
            data = data_

            //下游分析从数据库加载其它数据
        } else if (inputAnalysisMethod) {


            data = dataMap[inputAnalysisMethod]

        } else {
            if (dataKey_) {
                if (dataKey_ in dataMap) {
                    data = dataMap[dataKey_]
                }
            } else {
                if ("first_data_key" in dataMap) {
                    data = dataMap[dataMap['first_data_key']]
                } else {
                    // 上游分析的key
                    if (name in dataMap) {
                        data = dataMap[name]
                    }
                }
                // if (inputKey) {


                // } else {


                // }

            }
        }

        // else{
        //     console.log(dataKey)
        //     const values = dataKey['sample_group_list'].map(((it:any)=>it.content.reference))
        //     console.log(values)
        // }
        // console.log(data) 
        // console.log(dataMap[dataKey])
        return <Component {...rest} {...crest} data={data} name={name} />;
    };

    return <>
        {/* {JSON.stringify(formJson)} */}

        {formJson.map((it: any, index: any) => (
            <ComponentsRender key={index} {...it} dataMap={dataMap}></ComponentsRender>
        ))}

    </>
},
    (prevProps, nextProps) => {
        // console.log(prevProps)
        // console.log(nextProps)
        // // console.log("1111111111111111111"+(prevProps === nextProps))
        // // return prevProps === nextProps; // 自定义比较逻辑
        // console.log(prevProps)
        // console.log(nextProps)
        console.log(JSON.stringify(prevProps) === JSON.stringify(nextProps))
        return JSON.stringify(prevProps) === JSON.stringify(nextProps) // JSON.stringify(prevProps.formJson) === JSON.stringify(nextProps.formJson) 
    }
)

export default FormJsonComp

const FilterSelect: FC<any> = ({ label, name, data, rules, field, ...rest }) => {
    const [options, setOptions] = useState<any>()
    const form = Form.useFormInstance();

    useEffect(() => {
        // console.log(data)
        if (data && field) {
            const filterField: any = [...new Set(data.map(field))]
            const options = filterField.map((it: any) => {
                return {
                    label: it,
                    value: it
                }
            })
            setOptions(options)
            // setInitialValue(filterField[0])
            form.setFieldValue(name, filterField[0])
            // console.log(options)
        }
    }, [data])
    return <>
        <Form.Item label={label} name={name} rules={rules}>
            <BasicSelect {...rest} options={options}></BasicSelect>
        </Form.Item>
    </>
}
const BasicSelect: FC<any> = ({ options, clear, value, onChange, ...rest }) => {
    const form = Form.useFormInstance();

    const selectChange = (value: any) => {
        onChange(value)
        if (clear) {
            form.resetFields(clear)
        }
    }
    return <Select showSearch filterOption={(input: any, option: any) =>
        (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} {...rest} options={options} value={value} onChange={selectChange}></Select>
}


export const MetaphlanCladeSelect: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    const [options, setOptions] = useState<any>()
    const loadData = async () => {
        const resp: any = await axios.get(`/fast-api/get_metaphlan_clade`)
        let data: any = resp.data.map((it: any) => {
            return {
                label: `${it.taxon.replaceAll(" ", "_")}_${it.clade}`,
                value: it.clade
            }
        })
        // data =  [
        //     {
        //         label: "0.2",
        //         value: 0.2
        //     }, {
        //         label: "0",
        //         value: 0
        //     }
        // ]
        setOptions(data)
        // console.log(data)
    }
    useEffect(() => {
        loadData()
    }, [])
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <Select   {...rest} options={options} showSearch filterOption={(input: any, option: any) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}></Select>
        </Form.Item>
        {/* <Form.Item name={`${name}_`} label={`${label}_`}>
            <Input value={111}></Input>
        </Form.Item> */}
    </>
}
export const GroupCompareSelect: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    const form = Form.useFormInstance();
    const treatment_group = Form.useWatch(["sites1", "group"], form);
    const control_group = Form.useWatch(["sites2", "group"], form);
    const [query, setQuery] = useState<any>()
    useEffect(() => {
        if (treatment_group && control_group) {
            setQuery([
                {
                    label: `Prevalent in both sites`,
                    value: `Prevalent in both sites`
                }, {
                    label: `Prevalent in ${control_group.join("-")}`,
                    value: `Prevalent in ${control_group.join("-")}`
                }, {
                    label: `Prevalent in ${treatment_group.join("-")}`,
                    value: `Prevalent in ${treatment_group.join("-")}`
                }, {
                    label: `Not prevalent in either sites`,
                    value: `Not prevalent in either sites`
                }
            ])
        }
    }, [treatment_group, control_group])
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <Select showSearch filterOption={(input: any, option: any) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} {...rest} options={query}></Select>
        </Form.Item>
    </>
}
const BaseInput: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <TextArea {...rest} />
        </Form.Item>
    </>
}

const BaseInputNumber: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <InputNumber {...rest} />
        </Form.Item>
    </>
}
export const BaseSelect: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <BasicSelect {...rest} options={data}></BasicSelect>
            {/* <Select showSearch filterOption={(input: any, option: any) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} {...rest} options={data}></Select> */}
        </Form.Item>
    </>
}
export const GroupSelectSampleButton: FC<any> = ({ label, name, rules, data, filter, group, groupField: groupField_ }) => {
    const [sampleGrouped, setSampleGrouped] = useState<any>()
    const [options, setOptions] = useState<any>([])
    // const [sampleGroupedOptions, setSampleGroupedOptions] = useState<any>([])
    const form = Form.useFormInstance();
    let filterName: any = []
    if (filter) {
        filterName = filter.map((it: any) => it.name)
    }
    const customFilterValue = Form.useWatch((values) => {
        const data = Object.entries(values).filter(([key]) => filterName.includes(key))
        return Object.fromEntries(data)
    }, form);

    const groupField = Form.useWatch(group, form);

    const calculateGroup = (sampleGroup: any, groupField: any) => {

        const grouped = sampleGroup.reduce((acc: any, item: any) => {
            const key = item[groupField];
            if (!acc[key]) {
                acc[key] = [];
            }
            acc[key].push(item.value);
            return acc;
        }, {});
        setSampleGrouped(grouped)


    }
    useEffect(() => {
        if (filter && customFilterValue) {
            data = filter.reduce((result: any, filterHandle: any) => {
                return result.filter((item: any) => {
                    return filterHandle.method(item) === customFilterValue[filterHandle.name];
                });
            }, data);

            data = data.map((it: any) => {
                const { label, id, value, ...rest } = it
                return {
                    label: `${it.label}(${filter[0].method(it)})`,
                    value: it.value,
                    ...rest

                }
            })
            //    data = 
            // for (let i = 0; i < filter.length; i++) {
            //     const filterHandle: any = filter[i]
            //     const filterData = data.filter((it: any) => {
            //         return filterHandle.method(it) == customFilterValue[filterHandle.name]
            //     })
            //     console.log(filterData)
            // }
        }
        // console.log(data)
        // console.log(data)
        if (data && groupField_) {
            // console.log(data)
            calculateGroup(data, groupField_)
        } else {
            if (data && groupField) {
                calculateGroup(data, groupField)
            }
        }

        setOptions(data)
        // form.resetFields()
        // if (groupField && sampleGroup && sampleGroup.length > 0) {
        //     // console.log("2222222")
        //     const sampleGroupedOptions = calculateGroup(sampleGroup, groupField)
        //     setSampleGroupedOptions(sampleGroupedOptions)

        // }
    }, [data, groupField, customFilterValue])
    return <>
        <Form.Item label={label} name={[name, "sample"]} rules={rules}>
            <GroupSelectSample sampleGrouped={sampleGrouped} sampleGroup={options} watch={[name, "group"]}></GroupSelectSample>
        </Form.Item>
        <Form.Item label={label} name={[name, "group"]} rules={rules}>
            <GroupSelectButton sampleGrouped={sampleGrouped}></GroupSelectButton>
        </Form.Item>
    </>
}
export const SelectAll: FC<any> = ({ label, name, data, initialValue, rules, ...rest }) => {
    return <>
        <Form.Item initialValue={initialValue} label={label} name={name} rules={rules}>
            <SelectAllComp data={data} {...rest}></SelectAllComp>
        </Form.Item>
    </>
}
const SelectAllComp: FC<any> = ({ data, value, onChange, mode, ...rest }) => {
    const [selectedItems, setSelectedItems] = useState<any>(value);
    // const [options, setOptions] = useState<any>([]);
    const onChangeSelct = (value: any) => {
        console.log(value)
        onChange(value)
        setSelectedItems(value)
    }

    // useEffect(() => {
    //     setOptions(options)
    // }, [resultTableList])
    return <>

        <Select {...rest} mode={mode} value={selectedItems} onChange={onChangeSelct} allowClear options={data}></Select>
        {mode == "multiple" && <Button onClick={() => {
            const values = data.map((it: any) => it.value)
            // console.log(values)
            setSelectedItems(values)
            onChange(values)
        }}>选择全部{selectedItems && <>({selectedItems.length})</>}</Button>}
    </>
}



const GroupSelectSample: FC<any> = ({ value, onChange, sampleGroup, watch, sampleGrouped }) => {
    // const [options, setOptions] = useState<any>([])
    // const [groupedLabel,setGroupedLabel] = useState<any>([])
    // const [grouped, setGrouped] = useState<any>({})
    // const [groupedKey, setGroupedKey] = useState<any>({})
    const [group, setGroup] = useState<any>()

    const form = Form.useFormInstance();
    const group_ = Form.useWatch(watch, form);
    useEffect(() => {
        setGroup(group_)
    }, [group_])
    //
    //  const [optionsValues,setOptionsValues] = useState<any>(value)
    // useEffect(() => {
    //     const grouped = sampleGroup.reduce((acc: any, item: any) => {
    //         const key = item[group_field];
    //         if (!acc[key]) {
    //             acc[key] = [];
    //         }
    //         acc[key].push(item.value);
    //         return acc;
    //     }, {});
    //     setGrouped(grouped)
    //     // const groupedArray = Object.entries(grouped).map(([key, value])=>{
    //     //     return {
    //     //         label:key,
    //     //         value:key

    //     //     }
    //     // });
    //     // setGroupedLabel(groupedArray)
    //     // const options = sampleGroup.map((it: any) => {
    //     //     return {
    //     //         label: `${it.sample_key}(${it[group_field]})`,
    //     //         value: it.sample_key
    //     //     }
    //     // })
    //     // setOptions(options)
    // }, [sampleGroup, group_field])
    // const onSelectChange = (value: any) => {
    //     // const values = sampleGroup[value]
    //     // setOptionsValues(values)
    //     onChange(value)
    //     // console.log(group)
    //     console.log(value)
    // }
    const onSelectGroup = (keys: any) => {
        const merged = Object.entries(sampleGrouped ? sampleGrouped : {})
            .filter(([key]) => keys.includes(key)) // 只保留特定 key
            .flatMap(([, value]) => value);
        // console.log(merged)
        // const value = grouped[key]
        // console.log(value)
        onChange(merged)
        // setGroupedKey(key)
    }

    useEffect(() => {
        if (group) {
            // console.log(group)
            onSelectGroup(group)
        }
        // onSelectGroup(group)
    }, [group])
    return <>
        {/* {watch}{group} */}
        <Select showSearch filterOption={(input: any, option: any) =>
            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} mode={"multiple"} value={value} onChange={onChange} options={sampleGroup}></Select>
        {value && <>一共选择{value.length}个样本</>}

    </>
}
const GroupSelectButton: FC<any> = ({ value, onChange, sampleGrouped }) => {
    // const [options, setOptions] = useState<any>([])
    // const [groupedLabel,setGroupedLabel] = useState<any>([])
    // const [grouped, setGrouped] = useState<any>({})
    // const [groupedKey, setGroupedKey] = useState<any>(value ? value : [])

    //
    //  const [optionsValues,setOptionsValues] = useState<any>(value)
    // useEffect(() => {
    //     const grouped = sampleGroup.reduce((acc: any, item: any) => {
    //         const key = item[group_field];
    //         if (!acc[key]) {
    //             acc[key] = [];
    //         }
    //         acc[key].push(item.value);
    //         return acc;
    //     }, {});
    //     setGrouped(grouped)

    // }, [sampleGroup, group_field])

    const onSelectGroup = (key: any) => {

        if ((value ? value : []).includes(key)) {
            const currentKey = (value ? value : []).filter((it: any) => !it.includes(key))
            // setGroupedKey(currentKey)
            onChange(currentKey)
        } else {
            const currentKey = [...(value ? value : []), key]
            // setGroupedKey(currentKey)
            onChange(currentKey)
        }
        // console.log(currentKey)
        // setGroupedKey([key])

    }
    return <>
        {/* <Select mode={"multiple"} value={value} onChange={onSelectChange} options={options}></Select> */}
        {Object.entries(sampleGrouped ? sampleGrouped : {}).map(([key, value2]: any) => (<span key={key}>
            <Button type={(value ? value : []).includes(key) ? "primary" : "dashed"} onClick={() => onSelectGroup(key)}>{key}({value2.length})</Button>
        </span>))}
        {/* {groupedKey} */}

    </>
}