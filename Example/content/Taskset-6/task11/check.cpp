#include "testlib.h"
using namespace std;

struct Edge {
    int from, to;
};

int n, m, ori, s, t;
vector<Edge> edges;


int checkSolution(InStream &str) {
    int k = str.readInt(0, m+n+16, "number of paths");
    vector<bool> used(m, false);
    for (int i = 0; i < k; i++) {
        int q = str.readInt(0, m+n+16, format("path[%d] len", i));
        int curr = s;
        for (int j = 0; j < q; j++) {
            int from = str.readInt(1, n, format("from[%d,%d]", i, j)) - 1;
            int index = str.readInt(1, m, format("edge[%d,%d]", i, j)) - 1;
            int to = str.readInt(1, n, format("to[%d,%d]", i, j)) - 1;
            Edge e = edges[index];
            str.ensuref(
                (from == e.from && to == e.to) ||
                (from == e.to && to == e.from && !ori),
                "step[%d,%d]: edge (%d,%d) does not match printed (%d,%d)",
                i, j, e.from, e.to, from, to
            );
            str.ensuref(curr == from, "step[%d,%d]: from %d different from current vertex %d", i, j, from, curr);
            curr = to;
            str.ensuref(!used[index], "step[%d,%d]: edge %d (%d,%d) used second time", i, j, index, from, to);
            used[index] = true;
        }
        str.ensuref(curr == t, "path %d finished at %d instead of %d", i, curr, t);
    }
    return k;
}

int main(int argc, char **argv) {
    setName("edge paths checker");
    registerTestlibCmd(argc, argv);

    n = inf.readInt();
    m = inf.readInt();
    ori = inf.readInt();
    s = inf.readInt() - 1;
    t = inf.readInt() - 1;
    for (int i = 0; i < m; i++) {
        Edge e;
        e.from = inf.readInt() - 1;
        e.to = inf.readInt() - 1;
        edges.push_back(e);
    }

    int juryAns = checkSolution(ans);
    int partAns = checkSolution(ouf);

    if (partAns < juryAns)
        quitf(_wa, "Participant solution is worse: %d < %d", partAns, juryAns);
    if (partAns > juryAns)
        quitf(_fail, "Participant solution is BETTER: %d > %d", partAns, juryAns);

    quitf(_ok, "%d vertices, %d %s-edges, %d paths", n, m, (ori ? "ori" : "bid"), partAns);
}
