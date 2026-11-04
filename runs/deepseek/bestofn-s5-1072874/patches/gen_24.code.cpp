FIT_UINT16 Field::GetNumSubFields(void) const
{
    if (profile == NULL)
        return 0;
    const FIT_UINT16 numFields = profile->numFields;
    return (profileIndex < numFields) ? profile->fields[profileIndex].numSubFields : 0;
}
