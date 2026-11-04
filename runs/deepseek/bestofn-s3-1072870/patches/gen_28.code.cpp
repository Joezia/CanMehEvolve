FieldDefinition* MesgDefinition::GetFieldByIndex(const FIT_UINT16 index)
{
    FieldDefinition* const base = fields.data();
    const size_t count = fields.size();

    return (static_cast<size_t>(index) < count) ? (base + index) : FIT_NULL;
}
