FIT_UINT8 Field::GetType() const
{
    return (type != FIT_UINT8_INVALID) ? type : 
           ((profile == NULL || profileIndex >= profile->numFields) ? 
            FIT_UINT8_INVALID : profile->fields[profileIndex].type);
}
