FIT_FLOAT64 FieldBase::GetScale(const FIT_UINT16 subFieldIndex) const
{
    if (profile == NULL)
        return 1.0;

    if (subFieldIndex >= profile->num_subfields)
        return profile->scale;

    return profile->subfields[subFieldIndex].scale;
}
