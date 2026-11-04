
FIT_UINT16 Field::GetNumSubFields(void) const
{
    if (!profile) return 0;
    if (profileIndex >= profile->numFields) return 0;
    return profile->fields[profileIndex].numSubFields;
}
