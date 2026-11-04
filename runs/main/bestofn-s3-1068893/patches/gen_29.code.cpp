FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;
        
    if (profile == NULL)
        return FIT_UINT8_INVALID;
        
    return (profileIndex < profile->numFields) 
        ? profile->fields[profileIndex].type 
        : FIT_UINT8_INVALID;
}
