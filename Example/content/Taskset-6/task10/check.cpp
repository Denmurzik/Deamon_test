#include "testlib.h"
using namespace std;

int n;
vector<int> input;

int checkSolution(InStream &str) {
    int k = str.readInt(0, n, "Answer");

    vector<int> ids;
    for (int i = 0; i < k; i++) {
        string a = str.readToken();
        string b = str.readToken();
        string c = str.readToken();
        int idx, val;
        str.ensuref(b == "=", "%d: second token must be equal sign (%s)", i, b.c_str());
        str.ensuref(sscanf(a.c_str(), "A[%d]", &idx) == 1, "%d: cannot parse index (%s)", i, a.c_str());
        str.ensuref(sscanf(c.c_str(), "%d", &val) == 1, "%d: cannot parse value (%s)", i, c.c_str());
        str.ensuref(idx >= 1 && idx <= n, "%d: index %d out of range [1; %d]", i, idx, n);
        idx--;
        str.ensuref(input.at(idx) == val, "%d: value at index %d is %d instead of %d", i, idx, input.at(idx), val);
        ids.push_back(idx);
    }

    ensure(ids.size() == k);
    for (int i = 0; i+1 < k; i++) {
        int a = ids[i], b = ids[i+1];
        str.ensuref(a < b, "%d: next index is %d, not greater than %d", i, b, a);
        str.ensuref(input[a] < input[b], "%d: next value is %d (%d-th), not greater than %d (%d-th)", i, input[b], b, input[a], a);
    }

    return k;
}

int main(int argc, char **argv) {
    setName("longest increasing subsequence checker");
    registerTestlibCmd(argc, argv);

    n = inf.readInt();
    for (int i = 0; i < n; i++)
        input.push_back(inf.readInt());

    int juryAns = checkSolution(ans);
    int partAns = checkSolution(ouf);

    if (partAns < juryAns)
        quitf(_wa, "Participant solution is worse: %d < %d", partAns, juryAns);
    if (partAns > juryAns)
        quitf(_fail, "Participant solution is BETTER: %d > %d", partAns, juryAns);

    quitf(_ok, "%d: %d", n, partAns);
}
