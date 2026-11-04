
FIT_UINT16 Field::GetNumSubFields(void) const
{
    return (profile && profileIndex < profile->numFields) 
        ? profile->fields[profileIndex].numSubFields 
        : 0;
}
