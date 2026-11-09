
FIT_UINT16 Field::GetNumSubFields(void) const
{
    return (profile == NULL || profileIndex >= profile->numFields) ? 0 : profile->fields[profileIndex].numSubFields;
}
