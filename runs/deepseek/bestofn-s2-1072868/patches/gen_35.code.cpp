FIT_UINT16 Field::GetNumSubFields(void) const
{
    if (profile == NULL || profileIndex >= profile->numFields)
        return 0;
    return profile->fields[profileIndex].numSubFields;
}
