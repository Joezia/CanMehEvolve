FieldBase::FieldBase(const FieldBase &field)
{
    const auto valueCount = field.values.size();
    if (valueCount != 0)
    {
        values.assign(field.values.data(), field.values.data() + valueCount);
    }

    const auto indexCount = field.stringIndexes.size();
    if (indexCount != 0)
    {
        stringIndexes.assign(field.stringIndexes.data(), field.stringIndexes.data() + indexCount);
    }
}
