FieldDefinition* MesgDefinition::GetFieldByIndex(const FIT_UINT16 index)
{
    FieldDefinition* const fieldsData = fields.data();
    const auto fieldCount = fields.size();

    if (__builtin_expect(index < fieldCount, 1))
        return fieldsData + index;

    return FIT_NULL;
}
