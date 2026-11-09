FIT_FLOAT64 FieldBase::GetScale(const FIT_UINT16 subFieldIndex) const
{
    if (subFieldIndex >= num_subfields_)
        return scale_;

    const SubFieldBase* subfield = subfields_ + subFieldIndex;
    return NULL != subfield ? subfield->scale : 1.0;
}
